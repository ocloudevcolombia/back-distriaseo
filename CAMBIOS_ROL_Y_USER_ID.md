# Cambios: Campo `rol` y `user_id` en Pedidos

## Resumen de Cambios

Se han realizado los siguientes cambios en el backend:

### 1. Campo `rol` en la tabla `users`

- **Modelo**: `app/models/users/users.py`
  - Se agregó el campo `rol` (String(50), nullable=True, default="user")
  
- **Schema**: `app/schemas/users/users.py`
  - Se agregó `rol` en `UserCreate` (opcional, por defecto "user")
  - Se agregó `rol` en `UserRead` (opcional)

- **Servicio**: `app/services/user/users.py`
  - Se actualizó `register_user` para guardar el campo `rol`

**Uso**: Este campo permite validar en el frontend qué tipo de usuario es (ej: "admin", "user", "vendedor", etc.)

### 2. Campo `user_id` en la tabla `orders`

- **Modelo**: `app/models/store/orders/models.py`
  - Se agregó el campo `user_id` (Integer, ForeignKey a users.id, nullable=True)
  - Se agregó la relación `user` con el modelo User

- **Servicio**: `app/services/store/orders/orders.py`
  - Se actualizó `create_order` para recibir y guardar `user_id`

- **Endpoint**: `app/api/store/orders/orders.py`
  - Se actualizó `create_new_order` para obtener el usuario autenticado usando `get_current_active_user`
  - Ahora se guarda automáticamente el ID del usuario logueado cuando crea un pedido

- **Servicio de Facturas**: `app/services/store/sales/services.py`
  - Se actualizó `create_sale` para asignar `user_id` al pedido si no lo tiene

- **Endpoint de Facturas**: `app/api/store/sales/api.py`
  - Se actualizó `create_sale_endpoint` para obtener el usuario autenticado
  - Al crear una factura, se guarda el `user_id` del usuario logueado en el pedido

## Migraciones de Base de Datos

**⚠️ IMPORTANTE**: Después de estos cambios, necesitas crear y ejecutar una migración de Alembic para actualizar la base de datos.

### Pasos para crear la migración:

1. **Navegar al directorio del backend**:
   ```bash
   cd back/app
   ```

2. **Crear la migración automática**:
   ```bash
   alembic revision --autogenerate -m "Add rol to users and user_id to orders"
   ```

3. **Revisar el archivo de migración generado**:
   - Se creará un archivo en `alembic/versions/` con un nombre similar a `xxxxx_add_rol_to_users_and_user_id_to_orders.py`
   - Revisa que las operaciones sean correctas:
     - `alter_table('users')` con `add_column('rol')`
     - `alter_table('orders')` con `add_column('user_id')` y `create_foreign_key`

4. **Aplicar la migración**:
   ```bash
   alembic upgrade head
   ```

### Si no tienes Alembic configurado:

Si no tienes migraciones de Alembic configuradas, puedes ejecutar estos comandos SQL directamente:

```sql
-- Agregar campo rol a users
ALTER TABLE users ADD COLUMN rol VARCHAR(50) DEFAULT 'user';

-- Agregar campo user_id a orders
ALTER TABLE orders ADD COLUMN user_id INTEGER;
ALTER TABLE orders ADD CONSTRAINT fk_orders_user_id FOREIGN KEY (user_id) REFERENCES users(id);
```

**Nota**: Si ya tienes usuarios en la base de datos, puedes actualizar sus roles después:
```sql
UPDATE users SET rol = 'user' WHERE rol IS NULL;
UPDATE users SET rol = 'admin' WHERE is_admin = 1; -- Si quieres mantener consistencia
```

## Uso en el Frontend

### Campo `rol`

Ahora cuando obtengas el usuario actual (endpoint `/users/me`), recibirás:
```json
{
  "id": 1,
  "full_name": "Juan Pérez",
  "email": "juan@example.com",
  "rol": "admin"
}
```

Puedes usar este campo para validar permisos en el frontend:
```javascript
if (user.rol === 'admin') {
  // Mostrar opciones de administrador
}
```

### Campo `user_id` en Pedidos

Al obtener un pedido (endpoint `/orders/{order_id}`), ahora incluirá información del usuario que lo creó (a través de la relación). Esto te permite saber quién hizo cada pedido.

## Notas Importantes

1. **Autenticación requerida**: Ahora los endpoints de creación de pedidos y facturas requieren autenticación (token Bearer). Asegúrate de que el frontend envíe el token en los headers.

2. **Retrocompatibilidad**: Los campos `rol` y `user_id` son opcionales (nullable=True), por lo que no deberías tener problemas con datos existentes, pero ejecuta las migraciones para evitar errores.

3. **Valores por defecto**: Si no se proporciona un `rol` al crear un usuario, se asignará "user" por defecto.
