import zipfile

# Create a store.py zip for upload
with zipfile.ZipFile('store.py.zip', 'w') as z:
    z.write('store.py')
