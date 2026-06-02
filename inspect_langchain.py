import importlib
import langchain
print('langchain version:', getattr(langchain, '__version__', 'unknown'))
modules = [
    'langchain.embeddings',
    'langchain.embeddings.google',
    'langchain.embeddings.openai',
    'langchain.embeddings.google_retrieval',
    'langchain.embeddings.google_cloud',
]
for mod in modules:
    try:
        m = importlib.import_module(mod)
        print('module', mod, 'loaded')
        for name in dir(m):
            if 'Google' in name or 'Generative' in name or 'Embedding' in name:
                print(' ', name)
    except Exception as e:
        print('module', mod, 'failed', e)
