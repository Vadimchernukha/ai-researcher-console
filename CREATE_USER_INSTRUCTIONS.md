# 🔐 Создание пользователя lgchernukha@gmail.com

## 📋 **Инструкции:**

### 1. **Получите Service Role Key**
1. Откройте: https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv/settings/api
2. Скопируйте **service_role** ключ (не anon key!)

### 2. **Создайте пользователя**

#### Вариант A: Через терминал
```bash
# Установите переменную окружения
export SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"

# Создайте пользователя
python3 create_vadim_user.py
```

#### Вариант B: Через скрипт
```bash
# Запустите интерактивный скрипт
./create_user_quick.sh
```

### 3. **Данные пользователя:**
- **Email**: `lgchernukha@gmail.com`
- **Пароль**: `200815462Cv!`
- **Имя**: `Vadim Chernukha`
- **Роль**: `user`
- **Кредиты**: `100`

## 🚀 **Быстрое создание:**

```bash
# 1. Получите Service Role Key из Dashboard
# 2. Установите переменную
export SUPABASE_SERVICE_ROLE_KEY="your-key-here"

# 3. Создайте пользователя
python3 create_vadim_user.py
```

## ✅ **Проверка:**

После создания пользователя вы увидите:
```
✅ Пользователь создан с ID: [uuid]
✅ Профиль пользователя создан
📧 Email: lgchernukha@gmail.com
🔑 Пароль: 200815462Cv!
💳 Кредиты: 100
👑 Роль: user
```

## 🔗 **Полезные ссылки:**

- **Supabase Dashboard**: https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv
- **API Settings**: https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv/settings/api
- **Authentication**: https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv/auth/users

## 🎯 **Готово!**

Пользователь будет создан и готов к использованию в системе AI Researcher Console! 🎉
