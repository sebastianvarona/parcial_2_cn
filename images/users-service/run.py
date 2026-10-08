import os
from users.views import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', '3001'))
    app.run(host='0.0.0.0', port=port)
