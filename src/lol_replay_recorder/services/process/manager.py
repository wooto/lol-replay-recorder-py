import os
import subprocess
import signal
from typing import Any, Dict, Optional, TYPE_CHECKING

from .platform import PlatformResolver
from ...utils.utils import sleep_in_seconds
from ...domain.errors import CustomError, ProcessError

if TYPE_CHECKING:
    pass


class ProcessManager:
    """
    League 클라이언트 프로세스 관리 담당

    Riot 프로세스 시작, 중지 및 상태 관리를 담당합니다.
    Windows와 Unix/macOS에서 각각 다른 전략을 사용합니다.
    """

    def __init__(
        self,
        platform_resolver: PlatformResolver,
        window_client: Optional[Any] = None  # WindowHandler 또는 WindowAutomationClient
    ):
        """
        ProcessManager 초기화

        Args:
            platform_resolver: 플랫폼별 경로 및 설정 해결 도구
            window_client: 윈도우 자동화 클라이언트 (선택 사항)
        """
        self.platform = platform_resolver
        self.window_client = window_client

    async def start_safely(
        self,
        params: Dict[str, Any],
        max_attempts: int = 5
    ) -> None:
        """
        안전하게 Riot 프로세스를 시작합니다. 재시도 로직과 검증 포함.

        이 메서드는 LeagueClient.start_riot_processes_safely()에서 추출되었습니다.

        Args:
            params: Dictionary containing 'region' (Region), 'locale' (Locale),
                   'username' (str), and 'password' (str)
            max_attempts: 최대 시도 횟수 (기본값: 5)

        Raises:
            ProcessError: 프로세스 시작 실패 또는 상태 검증 실패 시
            CustomError: 로케일 검증 실패 시
        """
        # 기존 프로세스 정리
        await self.stop_riot_processes()

        # 로케일 설정은 호출하는 쪽에서 처리해야 함
        # LeagueClient에서 set_locale()이 이미 호출되었다고 가정

        # 지연 임포트로 순환 참조 방지
        from ...controllers.riot_game_client import RiotGameClient
        from ...controllers.league_client_ux import LeagueClientUx

        # 클라이언트 인스턴스 생성
        riot_client = RiotGameClient()
        league_ux = LeagueClientUx()

        for attempt in range(max_attempts):
            try:
                # Riot 클라이언트 시작 및 로그인
                await riot_client.start_riot_client(params["region"], params["locale"])
                await riot_client.login(params["username"], params["password"], params["region"])

                # 클라이언트 준비 대기
                await league_ux.wait_for_client_to_be_ready()

                # 클라이언트가 idle 상태인지 검증
                state = await league_ux.get_state({"retry": 1})
                if state.get("action") != "Idle":
                    raise ProcessError(f"Client is not ready: {state.get('action')}")

                break  # 성공 시 루프 탈출

            except Exception as e:
                print(f"Error starting Riot processes (attempt {attempt + 1}): {e}")
                if attempt < max_attempts - 1:  # 마지막 시도가 아니면 대기
                    await sleep_in_seconds(1)
                await self.stop_riot_processes()  # 실패 시 프로세스 정리

                if attempt == max_attempts - 1:
                    raise ProcessError(f"Failed to start Riot processes after {max_attempts} attempts: {e}")

        # 로케일이 올바르게 설정되었는지 검증
        region_locale = await league_ux.get_region_locale(30)
        if region_locale["locale"] != params["locale"]:
            raise CustomError(
                f"Locale is not correct: expected {params['locale']}, got {region_locale['locale']}"
            )

        await sleep_in_seconds(5)

    async def stop_windows_processes(self) -> None:
        """
        Windows에서 Riot 프로세스를 중지합니다.

        이 메서드는 LeagueClient._stop_windows_processes()에서 추출되었습니다.
        """
        processes = [
            "RiotClientUx.exe",
            "RiotClientServices.exe",
            "RiotClient.exe",
            "Riot Client.exe",
            "LeagueClient.exe",
            "League of Legends.exe",
            "LeagueClientUxRender.exe"
        ]

        # 프로세스 강제 종료
        for process in processes:
            try:
                subprocess.run(
                    f"taskkill /F /IM \"{process}\" /T",
                    shell=True,
                    capture_output=True
                )
            except Exception:
                pass  # 프로세스 종료 오류는 무시

        # 프로세스가 완전히 종료될 때까지 대기
        for process in processes:
            for _ in range(30):
                try:
                    result = subprocess.run(
                        f"tasklist /FI \"IMAGENAME eq {process}\"",
                        shell=True,
                        capture_output=True,
                        text=True
                    )
                    if process not in result.stdout:
                        break
                    await sleep_in_seconds(1)
                except Exception:
                    break

    async def stop_unix_processes(self) -> None:
        """
        Unix 시스템(macOS/Linux)에서 Riot 프로세스를 중지합니다.

        이 메서드는 LeagueClient._stop_unix_processes()에서 추출되었습니다.
        """
        process_names = [
            "LeagueClientUx",
            "RiotClientServices",
            "RiotClient",
            "LeagueClient",
            "League of Legends",
        ]

        for process_name in process_names:
            try:
                # 프로세스 찾기 및 종료
                result = subprocess.run(
                    ["pgrep", "-f", process_name],
                    capture_output=True,
                    text=True
                )

                if result.returncode == 0:
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        if pid.strip():
                            try:
                                os.kill(int(pid.strip()), signal.SIGTERM)
                            except (ValueError, ProcessLookupError):
                                pass

            except Exception:
                pass  # 오류 무시

            # 프로세스 종료 대기
            for _ in range(10):
                try:
                    result = subprocess.run(
                        ["pgrep", "-f", process_name],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode != 0:
                        break
                    await sleep_in_seconds(1)
                except Exception:
                    break

    async def stop_riot_processes(self) -> None:
        """
        모든 Riot 관련 프로세스를 중지하고 lockfile을 정리합니다.

        이 메서드는 LeagueClient.stop_riot_processes()에서 추출되었습니다.
        """
        if self.platform.is_windows():
            await self.stop_windows_processes()
        else:
            await self.stop_unix_processes()

        # 지연 임포트로 순환 참조 방지
        from ...controllers.riot_game_client import RiotGameClient
        from ...controllers.league_client_ux import LeagueClientUx

        # Lockfile 정리
        riot_client = RiotGameClient()
        league_ux = LeagueClientUx()

        try:
            await riot_client.remove_lockfile()
        except Exception:
            pass  # lockfile 제거 오류는 무시

        try:
            await league_ux.remove_lockfile()
        except Exception:
            pass  # lockfile 제거 오류는 무시