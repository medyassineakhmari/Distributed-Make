import os

# Liste des emojis et caractères "Box Drawing" à supprimer
# On garde les accents français (é, à, etc.)
BAD_CHARS = [
    '✅', '❌', '⚠️', '📊', '✓', '✗', '╔', '═', '║', '╚', '─', 
    '📋', '📝', '📁', '💡', '🚀', '🔥', 'ℹ️', '🛑', '🛌', '🧙', 
    '✨', '👮', '🚮', '📦', '🧪', '🏁', '🏆', '🎰', '💎', '📈',
    '🛌', '👋', '🛑', '🔒', '🔑'
]

# Dossiers à nettoyer
DIRS = ['Makefile/src', 'Makefile/performances/scripts']

def clean_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_len = len(content)
        
        # Suppression des caractères indésirables
        for char in BAD_CHARS:
            content = content.replace(char, '')
            
        # Si on a modifié le fichier
        if len(content) != original_len:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"cleaned: {filepath}")
            
    except Exception as e:
        print(f"Error reading {filepath}: {e}")

# Parcours récursif
for d in DIRS:
    for root, dirs, files in os.walk(d):
        for file in files:
            if file.endswith(('.java', '.py', '.sh', '.md')):
                clean_file(os.path.join(root, file))

print("Nettoyage terminé ! 🧹")
