import logging
from datetime import datetime
from datetime import datetime, timedelta, timezone
import math
import re
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction

logger = logging.getLogger(__name__)
DEFAULT_UNIT = 's'
UNIX_REGEX = '^\d{5,}$'
TIMESTAMP_REGEX_PARTS = [
    '\d{4}',
    '-\d{2}',
    '-\d{2}',
    '\s\d{2}',
    ':\d{2}',
    ':\d{2}'
]
TIMESTAMP_PATTERNS = [
    '%Y',
    '%Y-%m',
    '%Y-%m-%d',
    '%Y-%m-%d %H',
    '%Y-%m-%d %H:%M',
    '%Y-%m-%d %H:%M:%S',
]

class TimestampExtension(Extension):

    def __init__(self):
        logger.info('init Timestamp Extension')
        super(TimestampExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())

class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        items = []

        unit = extension.preferences.get('unit', DEFAULT_UNIT)
        unit_multiplier = 1000 if unit == 'ms' else 1

        arg = event.get_argument()

        if arg is None or arg.strip() == '':
            dt = datetime.now()
            ts = str(int(dt.timestamp()) * unit_multiplier)
            items.append(ExtensionResultItem(
                icon='images/icon.png',
                name="Timestamp: " + ts,
                description=dt.strftime('%Y-%m-%d %H:%M:%S'),
                highlightable=False,
                on_enter=CopyToClipboardAction(ts)
            ))
            return RenderResultListAction(items)

        if re.search(UNIX_REGEX, arg):
            ts = math.floor(int(event.get_argument()) / unit_multiplier)
            utcDt = datetime.utcfromtimestamp(ts)
            localDt = datetime.fromtimestamp(ts)

            formattedLocalDt = localDt.strftime('%Y-%m-%d %H:%M:%S')
            items.append(ExtensionResultItem(
                icon='images/icon.png',
                name="Local Time: " + formattedLocalDt,
                highlightable=False,
                on_enter=CopyToClipboardAction(formattedLocalDt)
            ))

            formattedUtcDt = utcDt.strftime('%Y-%m-%d %H:%M:%S')
            items.append(ExtensionResultItem(
                icon='images/icon.png',
                name="UTC Time: " + formattedUtcDt,
                highlightable=False,
                on_enter=CopyToClipboardAction(formattedUtcDt)
            ))
        else:
            parts_length = len(TIMESTAMP_REGEX_PARTS)
            for i in range(parts_length):
                date_regex = ''.join(TIMESTAMP_REGEX_PARTS[:parts_length - i])
                if re.search(f"^{date_regex}$", arg):
                    try:
                        localDt = datetime.strptime(arg, TIMESTAMP_PATTERNS[parts_length - 1 - i])
                        localTs = int(localDt.timestamp() * unit_multiplier)
                        items.append(ExtensionResultItem(
                            icon='images/icon.png',
                            name=f"As Local Time: {localTs}",
                            description=localDt.strftime('%Y-%m-%d %H:%M:%S'),
                            highlightable=False,
                            on_enter=CopyToClipboardAction(str(localTs))
                        ))
                        utcDt = datetime.strptime(arg, TIMESTAMP_PATTERNS[parts_length - 1 - i]).replace(tzinfo=timezone.utc)
                        utcTs = int(utcDt.timestamp() * unit_multiplier)
                        items.append(ExtensionResultItem(
                            icon='images/icon.png',
                            name=f"As UTC Time: {utcTs}",
                            description=utcDt.strftime('%Y-%m-%d %H:%M:%S'),
                            highlightable=False,
                            on_enter=CopyToClipboardAction(str(utcTs))
                        ))
                        break
                    except ValueError:
                        break

        return RenderResultListAction(items)

if __name__ == '__main__':
   TimestampExtension().run()
