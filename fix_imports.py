import os
import re

def fix_imports_in_file(file_path):
    """Arregla los imports en un archivo específico"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Backup del contenido original
        original_content = content
        
        # Patrones de imports incorrectos y sus correcciones
        import_fixes = [
            (r'^from core\.', 'from app.core.'),
            (r'^from models\.', 'from app.models.'),
            (r'^from schemas\.', 'from app.schemas.'),
            (r'^from utils\.', 'from app.utils.'),
            (r'^from api\.', 'from app.api.'),
            (r'^from services\.', 'from app.services.'),
            (r'^from database\.', 'from app.database.'),
            (r'^import core\.', 'import app.core.'),
            (r'^import models\.', 'import app.models.'),
            (r'^import schemas\.', 'import app.schemas.'),
            (r'^import utils\.', 'import app.utils.'),
            (r'^import api\.', 'import app.api.'),
            (r'^import services\.', 'import app.services.'),
        ]
        
        changes_made = []
        
        # Aplicar cada corrección línea por línea
        lines = content.split('\n')
        for i, line in enumerate(lines):
            original_line = line
            for pattern, replacement in import_fixes:
                if re.match(pattern, line.strip()):
                    new_line = re.sub(pattern, replacement, line)
                    if new_line != line:
                        lines[i] = new_line
                        changes_made.append(f"  Línea {i+1}: {original_line.strip()} → {new_line.strip()}")
                        break
        
        # Si hubo cambios, guardar el archivo
        if changes_made:
            new_content = '\n'.join(lines)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"\n✅ {file_path}")
            for change in changes_made:
                print(change)
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Error procesando {file_path}: {e}")
        return False

def main():
    """Procesa todos los archivos Python en el proyecto"""
    
    # Carpeta raíz del proyecto (donde está app/)
    project_root = "."
    app_folder = os.path.join(project_root, "app")
    
    if not os.path.exists(app_folder):
        print("❌ No se encontró la carpeta 'app/'. ¿Estás en la carpeta correcta?")
        print("   Debes ejecutar este script desde la carpeta 'back/'")
        return
    
    print("🔧 Reparando imports en todo el proyecto...")
    print("=" * 50)
    
    files_processed = 0
    files_changed = 0
    
    # Recorrer todos los archivos .py en app/
    for root, dirs, files in os.walk(app_folder):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                file_path = os.path.join(root, file)
                files_processed += 1
                
                if fix_imports_in_file(file_path):
                    files_changed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Resumen:")
    print(f"   Archivos procesados: {files_processed}")
    print(f"   Archivos modificados: {files_changed}")
    
    if files_changed > 0:
        print(f"\n✅ ¡Imports reparados! Ahora intenta:")
        print(f"   uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload")
    else:
        print(f"\nℹ️  No se encontraron imports para reparar.")

if __name__ == "__main__":
    main()