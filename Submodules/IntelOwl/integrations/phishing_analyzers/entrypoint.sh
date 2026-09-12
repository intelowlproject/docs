#!/bin/sh
/usr/bin/mkdir -p /var/log/intel_owl/phishing_analyzers
/usr/bin/touch /var/log/intel_owl/phishing_analyzers/gunicorn_access.log \
      /var/log/intel_owl/phishing_analyzers/gunicorn_errors.log
/usr/bin/chown -R phishing-user:phishing-user \
      /opt/deploy/phishing_analyzers /var/log/intel_owl/phishing_analyzers

exec gosu "${USER}" /usr/local/bin/gunicorn 'app:app' \
    --bind '0.0.0.0:4005' \
    --log-level "${LOG_LEVEL}" \
    --access-logfile /var/log/intel_owl/phishing_analyzers/gunicorn_access.log \
    --error-logfile /var/log/intel_owl/phishing_analyzers/gunicorn_errors.log