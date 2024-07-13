# /bin/bash 

djlint ./templates --reformat --format-css --format-js
djlint ./unicorn/templates/unicorn --reformat --format-css --format-js
autopep8 --recursive --in-place --exclude venv,.git ./  