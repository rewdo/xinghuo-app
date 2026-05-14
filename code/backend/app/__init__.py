from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from redis import StrictRedis
from config.default import Config

db = SQLAlchemy()
migrate = Migrate()
redis_client = StrictRedis()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # Initialize Redis (optional — graceful fallback if Redis is not running)
    global redis_client
    try:
        redis_client = StrictRedis.from_url(app.config['REDIS_URL'], decode_responses=True)
        redis_client.ping()
        app.logger.info('Redis connected')
    except Exception as e:
        app.logger.warning(f'Redis not available ({e}), using fallback')
        from redis import Redis
        redis_client = None

    # Register blueprints
    from app.api.user import user_bp
    from app.api.task import task_bp
    from app.api.order import order_bp
    from app.api.merchant import merchant_bp
    from app.api.wallet import wallet_bp
    from app.api.review import review_bp

    app.register_blueprint(user_bp, url_prefix='/api/v1/user')
    app.register_blueprint(task_bp, url_prefix='/api/v1/tasks')
    app.register_blueprint(order_bp, url_prefix='/api/v1/orders')
    app.register_blueprint(merchant_bp, url_prefix='/api/v1/merchant')
    app.register_blueprint(wallet_bp, url_prefix='/api/v1/wallet')
    app.register_blueprint(review_bp, url_prefix='/api/v1/reviews')

    # Health check
    @app.route('/api/health')
    def health():
        return {'status': 'ok', 'service': 'xinghuo-api'}

    return app
