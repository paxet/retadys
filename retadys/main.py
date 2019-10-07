import sys
import gunicorn.app.wsgiapp as wsgi

sys.argv.append('-b 127.0.0.1:5000')
sys.argv.append('retadys:app')
sys.exit(wsgi.run())
