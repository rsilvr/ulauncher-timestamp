import logging
import datetime
import math
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction

logger = logging.getLogger(__name__)
DEFAULT_UNIT = 's'

class TimestampExtension(Extension):

    def __init__(self):
        logger.info('init Timestamp Extension')
        super(TimestampExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())

class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        items = []

        unit = extension.preferences.get('unit', DEFAULT_UNIT)
        is_ms = unit == 'ms'

        if event.get_argument() is None:
            dt = datetime.datetime.now()
            ts = str(int(dt.timestamp()) * (1000 if is_ms else 1))
            items.append(ExtensionResultItem(
                icon='images/icon.png',
                name="Timestamp: " + ts,
                description=dt.strftime('%Y-%m-%d %H:%M:%S'),
                highlightable=False,
                on_enter=CopyToClipboardAction(ts)
            ))
            return RenderResultListAction(items)

        ts = math.floor(int(event.get_argument()) / (1000 if is_ms else 1))
        utcDt = datetime.datetime.utcfromtimestamp(ts)
        localDt = datetime.datetime.fromtimestamp(ts)

        formattedLocalDt = localDt.strftime('%Y-%m-%d %H:%M:%S')
        formattedUtcDt = utcDt.strftime('%Y-%m-%d %H:%M:%S')
        items.append(ExtensionResultItem(
            icon='images/icon.png',
            name="Local Time: " + formattedLocalDt,
            highlightable=False,
            on_enter=CopyToClipboardAction(formattedLocalDt)
        ))

        items.append(ExtensionResultItem(
            icon='images/icon.png',
            name="UTC Time: " + formattedUtcDt,
            highlightable=False,
            on_enter=CopyToClipboardAction(formattedUtcDt)
        ))

        return RenderResultListAction(items)

if __name__ == '__main__':
   TimestampExtension().run()
