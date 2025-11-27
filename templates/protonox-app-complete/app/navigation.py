from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty


class NavigationManager:
    """Centralized navigation stack with loading/error state hooks."""

    def __init__(self):
        self.manager = ScreenManager()
        self.loading_state = StringProperty("idle")
        self.error_message = StringProperty("")

    def build_initial_screen(self) -> Screen:
        from .login.login_view import LoginView
        from .login.register_view import RegisterView
        from .login.recover_view import RecoverView
        from .home.home_view import HomeView
        from .payments.pay_view import PayView
        from .reports.reports_view import ReportsView

        for view in [LoginView, RegisterView, RecoverView, HomeView, PayView, ReportsView]:
            self.manager.add_widget(view())
        self.manager.current = "login"
        return self.manager

    def navigate(self, screen_name: str) -> None:
        if screen_name in self.manager.screen_names:
            self.manager.current = screen_name
        else:
            self.error_message = f"Screen '{screen_name}' not found"
