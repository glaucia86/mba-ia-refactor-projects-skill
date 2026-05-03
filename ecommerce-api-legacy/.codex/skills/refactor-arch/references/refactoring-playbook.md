# Refactoring Playbook

Apply these transformations in Phase 3 after confirmation.

## 1. Hardcoded Config -> Settings Module

Before:

```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.run(debug=True)
```

After:

```python
from config.settings import SECRET_KEY, DEBUG
app.config["SECRET_KEY"] = SECRET_KEY
app.run(debug=DEBUG)
```

## 2. Concatenated SQL -> Parameterized Query

Before:

```python
cursor.execute("SELECT * FROM usuarios WHERE email = '" + email + "'")
```

After:

```python
cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
```

## 3. Arbitrary SQL Endpoint -> Remove or Guard

Before:

```python
cursor.execute(request.json["sql"])
```

After:

```python
return jsonify({"erro": "Endpoint administrativo desabilitado"}), 403
```

Only keep the endpoint when an authenticated authorization layer already exists.

## 4. Fat Route -> Route + Controller

Before:

```javascript
app.post('/api/checkout', (req, res) => {
  // validation, payment, enrollment, audit and response
});
```

After:

```javascript
router.post('/api/checkout', checkoutController.checkout);
```

```javascript
async function checkout(req, res, next) {
  const result = await checkoutService.checkout(req.body);
  res.status(200).json(result);
}
```

## 5. God Manager -> Domain Modules

Before:

```javascript
class AppManager {
  initDb() {}
  setupRoutes(app) {}
}
```

After:

```text
database/connection.js
models/courseModel.js
controllers/checkoutController.js
routes/checkoutRoutes.js
```

## 6. Query in Loop -> Join or Batch

Before:

```python
for item in itens:
    cursor.execute("SELECT nome FROM produtos WHERE id = ?", (item["produto_id"],))
```

After:

```python
cursor.execute("""
    SELECT i.*, p.nome AS produto_nome
    FROM itens_pedido i
    LEFT JOIN produtos p ON p.id = i.produto_id
    WHERE i.pedido_id = ?
""", (pedido_id,))
```

## 7. Deprecated ORM API -> Current Session API

Before:

```python
task = Task.query.get(task_id)
```

After:

```python
task = db.session.get(Task, task_id)
```

## 8. Weak Password Hashing -> Framework Hashing

Before:

```python
self.password = hashlib.md5(pwd.encode()).hexdigest()
```

After:

```python
from werkzeug.security import generate_password_hash, check_password_hash
self.password = generate_password_hash(pwd)
```

## 9. Sensitive Serializer -> Safe DTO

Before:

```python
return {"email": self.email, "password": self.password}
```

After:

```python
return {"id": self.id, "email": self.email, "role": self.role}
```

## 10. Bare Exception -> Central Error Handler

Before:

```python
except Exception as e:
    return jsonify({"erro": str(e)}), 500
```

After:

```python
except Exception:
    current_app.logger.exception("Unhandled request error")
    return jsonify({"erro": "Erro interno"}), 500
```

## 11. Duplicated Validation -> Helper

Before:

```python
if status not in ["pending", "in_progress", "done", "cancelled"]:
    return error
```

After:

```python
def validate_status(status):
    return status in TASK_STATUSES
```

## 12. Legacy Field Names -> Compatibility Adapter

Before:

```javascript
const email = req.body.eml;
```

After:

```javascript
const email = body.email ?? body.eml;
```

Use this when public request examples use legacy names.
