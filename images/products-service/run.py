import os
from products.views import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', '3002'))
    app.run(host='0.0.0.0', port=port)
