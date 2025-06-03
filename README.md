<h1 align="center">🔋 Gestión de Vehículos Eléctricos y Baterías 🔌</h1>
<h3 align="center">Un proyecto moderno con FastAPI, SQLAlchemy, Supabase y PostgreSQL</h3>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue?logo=python&style=flat"/>
  <img src="https://img.shields.io/badge/FastAPI-0.110.0-teal?logo=fastapi"/>
  <img src="https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql"/>
  <img src="https://img.shields.io/badge/Supabase-Storage-green?logo=supabase"/>
  <img src="https://img.shields.io/badge/Render-Deployed-blueviolet?logo=render"/>
</p>

---

## 📌 Descripción

Este sistema permite gestionar un inventario de vehículos eléctricos y sus respectivas baterías, con relaciones uno a uno, funcionalidades de filtrado, asociación/desasociación, estadísticas y gestión de imágenes en Supabase.

## 🚀 Tecnologías utilizadas

- ⚡️ **FastAPI** para la API backend
- 🐘 **PostgreSQL** como base de datos relacional
- 🧠 **SQLAlchemy** + **SQLModel** para modelos y ORM
- ☁️ **Render** para el despliegue en la nube
- 🖼️ **Supabase Storage** para guardar imágenes de vehículos
- 🌐 **Jinja2 + Bootstrap** para las vistas web

---

## 📂 Características principales

- **CRUD completo** para vehículos y baterías
- **Soft delete** para evitar la pérdida de datos
- **Subida y eliminación de imágenes** sincronizadas con Supabase
- **Dashboard de estadísticas** con métricas clave:
  - Total de vehículos y baterías
  - Porcentaje de baterías en mal estado
- **Filtrado por marca**
- **Asociación uno a uno** entre vehículo y batería
- **Recuperación de registros eliminados**
- **Vistas con Jinja2 y Bootstrap**


