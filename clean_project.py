import os

# Liste des emojis et caractères "Box Drawing" détectés dans ton grep
BAD_CHARS = [
    '✅', '❌', '⚠️', '📊', '✓', '✗', 
    '╔', '═', '║', '╚', '─', 
    '📋', '📝', '📁', '💡', '🚀', '🔥', 'ℹ️'
]

# Dossiers ciblés (selon ton grep)
TARGET_DIRS = [
    'Makefile/src', 
    'Makefile/performances/scripts'
]

def clean_file(filepath):
    # On ne touche pas aux images ou binaires
    if filepath.endswith(('.png', '.jpg', '.class', '.jar')):
        return

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 1. Suppression des caractères spéciaux
        for char in BAD_CHARS:
            content = content.replace(char, '')
            
        # 2. Si le fichier a changé, on sauvegarde
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✨ Nettoyé: {filepath}")
            
    except Exception as e:
        pass # On ignore les erreurs de lecture (fichiers binaires etc)

# Parcours récursif
print("Démarrage du nettoyage...")
for d in TARGET_DIRS:
    if os.path.exists(d):
        for root, dirs, files in os.walk(d):
            for file in files:
                clean_file(os.path.join(root, file))

print("Terminé.")
