npm run build
mv build/index.html ../bluejay/static/index.html
rm -rf ../bluejay/static/css
mv build/static/css ../bluejay/static/css
rm -rf ../bluejay/static/js
mv build/static/js ../bluejay/static/js
