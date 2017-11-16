"""All visbrain modules based on PyQt5 should inherit from PyQtModule."""
import os
import sip
from PyQt5 import QtGui
import logging

from .utils import set_widget_size, set_log_level, get_data_path
from .config import PROFILER, PYQT_APP, VISPY_APP, CONFIG
from .io import is_faulthandler_installed

sip.setdestroyonexit(False)
logger = logging.getLogger('visbrain')


class PyQtModule(object):
    """Shared methods across PyQt based Visbrain modules.

    Parameters
    ----------
    verbose : logging.level | None
        Verbosity level.
    to_describe : string | None
        The parent node to describe. Only available if verbose level is on
        debug.
    icon : str | None
        Name of the icon to use.
    """

    def __init__(self, verbose=None, to_describe=None, icon=None,
                 show_settings=True):
        """Init."""
        # Log level and profiler creation (if verbose='debug')
        set_log_level(verbose)
        if (logger.level == 10) and is_faulthandler_installed():
            import faulthandler
            faulthandler.enable()
            logger.debug("Faulthandler enabled")
        self._need_description = to_describe
        if isinstance(self._need_description, str):
            self._need_description = [self._need_description]
        self._module_icon = icon
        self._show_settings = show_settings

    def _pyqt_title(self, title, msg, symbol='='):
        """Define a PyQt title."""
        assert isinstance(title, str) and isinstance(symbol, str)
        n_symbol = 60
        start_title = int((n_symbol / 2) - (len(title) / 2)) - 1
        upper_bar = symbol * n_symbol
        title_bar = ' ' * start_title + title
        title_template = "\n%s\n%s\n\n{msg}" % (upper_bar, title_bar)
        logger.profiler(title_template.format(msg=msg))

    def show(self):
        """Display the graphical user interface."""
        # Fixed size for the settings panel :
        if hasattr(self, 'q_widget'):
            set_widget_size(PYQT_APP, self.q_widget, 23)
            self.q_widget.setVisible(self._show_settings)
        # Force the quick settings tab to be on the first tab :
        if hasattr(self, 'QuickSettings'):
            self.QuickSettings.setCurrentIndex(0)
        # Set icon (if possible) :
        if isinstance(self._module_icon, str):
            path_ico = get_data_path(folder='icons', file=self._module_icon)
            if os.path.isfile(path_ico):
                app_icon = QtGui.QIcon()
                app_icon.addFile(path_ico)
                self.setWindowIcon(app_icon)
            else:  # don't crash just for an icon...
                logger.debug("No icon found (%s)" % self._module_icon)
        else:
            logger.debug("No icon passed as an input.")
        # Tree description if log level is on debug :
        if isinstance(self._need_description, list):
            for k in self._need_description:
                self._pyqt_title('Tree', eval('self.%s.describe_tree()' % k))
        # Show and maximized the window :
        if PROFILER and logger.level == 1:
            self._pyqt_title('Profiler', '')
            PROFILER.finish()
        # If PyQt GUI :
        if CONFIG['SHOW_PYQT_APP']:
            self.showMaximized()
            VISPY_APP.run()

    def closeEvent(self, event):  # noqa
        """Executed method when the GUI closed."""
        PYQT_APP.quit()
        logger.debug("App closed.")