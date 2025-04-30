import panel as pn
from tornado.ioloop import IOLoop
from abc import ABC, abstractmethod
from jinja2 import Template
from param.parameterized import Event
from typing import Optional
from functools import partial


class PanelAbstract(ABC):
    @property
    @abstractmethod
    def is_root(self):
        """Show if panel is root panel."""

    @property
    @abstractmethod
    def template(self):
        """Navigation bar element template."""

    @property
    @abstractmethod
    def href(self):
        """Navigation bar element href."""

    @property
    @abstractmethod
    def title(self):
        """Navigation bar element title."""

    @abstractmethod
    def build_template(self):
        """Template initialize method."""

    @abstractmethod
    def add_sidebar(self, sidebar_html):
        """Add sidebar to the template."""


class Panel(PanelAbstract, ABC):
    def __init__(self):
        self._root = False
        self._template = pn.template.MaterialTemplate(title=self.title)

        self.build_template()

    def get_page(self):
        return self._template

    def add_sidebar(self, sidebar_html):
        navigation_bar = pn.pane.HTML(sidebar_html)
        self._template.sidebar.append(navigation_bar)
        self._template.sidebar_width = 150

    @property
    def is_root(self):
        return self._root

    @property
    def template(self):
        return self._template


class Articles(Panel):
    href = "articles"
    title = "Articles"

    def __init__(self):
        self._session_control_col: Optional[pn.Column] = None

        super().__init__()

    def _filter_protocols(self, event: Event = None, **kwargs):
        pass

    def _clean_articl_list(self):
        try:
            if "Articles" in self._session_control_col[-1][0].title:
                print("Cleaning article list")
                self._session_control_col.pop(-1)
        except AttributeError:
            pass
        except TypeError:
            pass

    def _get_articles(
        self,
        event: Event = None,
    ):
        self._clean_articl_list()

        self._article_name = pn.widgets.TextInput(name="Article name")
        articles_card = pn.Card(
            self._article_name,
            title="Articles",
            styles={"background": "WhiteSmoke"},
        )

        filter_article_by_name = pn.widgets.TextInput(
            name="Filter by article name",
            placeholder="Enter article name",
        )
        submit_filter_button = pn.widgets.Button(
            name="Filter",
            button_type="primary",
            on_click=partial(
                self._filter_protocols,
                filter_by_name=filter_article_by_name,
            ),
        )
        filters_card = pn.Card(
            filter_article_by_name,
            submit_filter_button,
            title="Filters",
            styles={"background": "WhiteSmoke"},
        )
        articles_column = pn.Column(
            articles_card,
            filters_card,
        )
        print("-----------\n", self._session_control_col)
        self._session_control_col.append(articles_column)

    def build_template(self):
        start_local_session_btn = pn.widgets.Button(
            name="Start local session",
            on_click=partial(
                self._get_articles,
            ),
        )
        self._session_control_col = pn.Column(start_local_session_btn)
        self._template.main.append(self._session_control_col)


class Settings(Panel):
    href = "settings"
    title = "Settings"

    def build_template(self):
        self._template.main.append(
            pn.pane.Markdown(
                """
                ## Settings
                This is the settings page.
                """
            )
        )


def get_navigation_bar_html(panel_list: list[Panel]):
    navigation_bar_template = """
    <ul>
        {% for href, title in items %}
            <li><a href="{{ href }}">{{ title }}</a></li>
        {% endfor %}
    </ul>
    """
    li_elements = [
        (panel.href, panel.title) if not panel.is_root else ("/", panel.title)
        for panel in panel_list
    ]
    template = Template(navigation_bar_template)
    navigation_bar_html = template.render(items=li_elements)
    return navigation_bar_html


loop = IOLoop.current()

articles = Articles()
settings = Settings()
panels = [articles, settings]

navigation_bar_html = get_navigation_bar_html(panels)
for panel in panels:
    panel.add_sidebar(navigation_bar_html)

panel_routes = dict()
for panel in panels:
    panel_routes[panel.href] = panel.get_page
    if panel.is_root:
        panel_routes[""] = panel.get_page


pn.serve(panels=panel_routes, loop=loop)
