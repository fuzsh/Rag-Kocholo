import logging
import colorama
import structlog


class LoggingConfigurator:
    _is_configured = False

    @classmethod
    def configure_logging(cls):
        if cls._is_configured:
            return

        # Configure the root logger
        logging.basicConfig(
            format="%(message)s",
            level=logging.INFO,
        )
        cr = structlog.dev.ConsoleRenderer(
            columns=[
                # Render the timestamp without the key name in yellow.
                structlog.dev.Column(
                    "timestamp",
                    structlog.dev.KeyValueColumnFormatter(
                        key_style=None,
                        value_style=colorama.Fore.YELLOW,
                        reset_style=colorama.Style.RESET_ALL,
                        value_repr=str,
                    ),
                ),
                # Render the event without the key name in bright magenta.
                structlog.dev.Column(
                    "event",
                    structlog.dev.KeyValueColumnFormatter(
                        key_style=None,
                        value_style=colorama.Style.BRIGHT + colorama.Fore.MAGENTA,
                        reset_style=colorama.Style.RESET_ALL,
                        value_repr=str,
                    ),
                ),
                # Default formatter for all keys not explicitly mentioned. The key is
                # cyan, the value is green.
                structlog.dev.Column(
                    "",
                    structlog.dev.KeyValueColumnFormatter(
                        key_style=colorama.Fore.CYAN,
                        value_style=colorama.Fore.GREEN,
                        reset_style=colorama.Style.RESET_ALL,
                        value_repr=str,
                    ),
                ),
            ]
        )

        # Define the processors for structlog
        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.StackInfoRenderer(),
                structlog.dev.set_exc_info,
                structlog.processors.TimeStamper(fmt="%Y-%m-%d", utc=False),
                structlog.dev.ConsoleRenderer()
            ],
            wrapper_class=structlog.make_filtering_bound_logger(logging.NOTSET),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=False
        )

        # structlog.configure(processors=structlog.get_config()["processors"][:-1]+[cr])

        cls._is_configured = True

    @classmethod
    def get_logger(cls, name=None):
        if not cls._is_configured:
            cls.configure_logging()

        return structlog.get_logger(name)
