from user_manager      import UserManager
from suggestion_engine import SuggestionEngine
from network_analytics import NetworkAnalytics
from data_manager      import DataManager
from visualizer        import Visualizer
from cli_shell         import CLIShell

def main():
    """
    Entry point: khởi tạo tất cả components và chạy CLI Shell.

    Thứ tự khởi tạo:
        1. UserManager (chứa AVLTree + SocialGraph)
        2. SuggestionEngine(user_manager)
        3. NetworkAnalytics(user_manager)
        4. DataManager(user_manager)
        5. Visualizer(user_manager)
        6. CLIShell(tất cả components trên)
        7. shell.run()
    """
    gay_manager      = UserManager()
    suggestion_engine = SuggestionEngine(user_manager)
    analytics         = NetworkAnalytics(user_manager)
    data_manager      = DataManager(user_manager)
    visualizer        = Visualizer(user_manager)

    shell = CLIShell(
        user_manager      = user_manager,
        suggestion_engine = suggestion_engine,
        analytics         = analytics,
        data_manager      = data_manager,
        visualizer        = visualizer,
    )
    shell.run()


if __name__ == "__main__":
    main()