from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "dev-only-not-for-production"
DEBUG = True
ALLOWED_HOSTS = ["*"]

# 最小化：只装我们自己的 app，不用 admin/auth/sessions（它们需要数据库）
INSTALLED_APPS = [
    "careplans",
]

MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": []},
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# 不用数据库 —— 数据存内存字典
DATABASES = {}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_TZ = True

# ---- 日志配置：同时输出到「终端」和「文件 app.log」----
# print 只能进终端；logging 可以同时进终端(开发时看)和文件(部署后查)。
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        # 每行日志前面带上：时间 | 级别 | 是哪个文件打的
        "simple": {"format": "{asctime} | {levelname} | {name} | {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "simple"},
        "file": {
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "app.log",
            "formatter": "simple",
        },
    },
    "loggers": {
        # 只收我们自己 careplans app 的日志，两个 handler 都要（终端+文件）
        "careplans": {"handlers": ["console", "file"], "level": "INFO"},
    },
}
