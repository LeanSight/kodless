# Investigación WYSIWID - Kodless

Esta carpeta contiene documentación de investigación sobre el patrón arquitectural **WYSIWID (What You See Is What It Does)** desarrollado por Daniel Jackson y Eagon Meng en MIT CSAIL.

## 📚 Documentos Disponibles

### 1. [wysiwid-ejemplos-diagramas-mermaid.md](wysiwid-ejemplos-diagramas-mermaid.md) (34KB)
**Ejemplos Reales con Diagramas Mermaid.js**

Documento completo con 40+ diagramas visuales en Mermaid.js que explican:
- ✅ Comparaciones arquitecturales (Traditional vs WYSIWID)
- ✅ Ejemplos reales: RealWorld/Conduit, Instagram-like
- ✅ Flujos de datos y CRUD operations
- ✅ El problema del "Favoriting"
- ✅ Ventajas para desarrollo con LLMs
- ✅ Comparación con microservicios
- ✅ Casos de uso: e-commerce, educación, healthcare
- ✅ Guía de migración
- ✅ Debugging con provenance

**📊 Ideal para**: Visualizar diferencias, presentaciones, entender arquitectura

---

### 2. [codigo-ejecutable-wysiwid.md](codigo-ejecutable-wysiwid.md) (31KB)
**Código Ejecutable y Diagramas Técnicos**

Implementaciones reales en TypeScript extraídas de repositorios MIT:
- Concepto User completo (con tests unitarios)
- Concepto Post completo
- Concepto Comment con threading
- Routes como sincronizaciones (Express)
- Motor de sincronizaciones (Sync Engine)
- DSL de sincronizaciones
- Sistema de provenance y debugging
- Ejemplo completo: Blog con comentarios

**💻 Ideal para**: Implementación, desarrollo, testing

---

### 3. [ejemplos-software-diagramas-wysiwid.md](ejemplos-software-diagramas-wysiwid.md) (36KB)
**Ejemplos de Software Reales y Diagramas**

Guía práctica con ejemplos concretos:
- Arquitectura conceptual con diagramas ER
- Kodless: El prototipo original (MIT)
- Conception: POC de aplicación modular
- RealWorld/Conduit: Caso de estudio del paper
- Fritter: Proyecto educativo MIT 6.1040
- DSL de sincronizaciones con sintaxis
- Características técnicas (URIs, provenance)
- Conceptos comunes reutilizables
- Comparación antes/después
- Recursos y materiales

**🎯 Ideal para**: Casos de uso prácticos, aprendizaje, repositorios reales

---

### 4. [compass_artifact_wf-*.md](compass_artifact_wf-35409fa9-24cb-491d-8bf2-aa212bf63657_text_markdown.md) (24KB)
**Investigación Completa del Paper**

Análisis académico detallado del paper WYSIWID:
- Contexto y autores (Daniel Jackson, Eagon Meng)
- El problema central: software "ilegible"
- La solución: Concepts + Synchronizations
- Análisis crítico y evaluación académica
- Comentarios de expertos (Kevin Sullivan, Thomas Ball)
- Implementaciones ejecutables y repositorios
- Materiales suplementarios (charlas, videos, libro)
- Direcciones futuras
- Impacto educativo (MIT 6.1040)

**📖 Ideal para**: Contexto teórico, fundamentos académicos, referencias

---

## 🎯 Cómo Usar Esta Documentación

### Si eres nuevo en WYSIWID:
1. **Empieza con**: `wysiwid-ejemplos-diagramas-mermaid.md` (sección 1-3)
   - Ver diagramas visuales de arquitectura
   - Entender diferencias con arquitecturas tradicionales

2. **Continúa con**: `ejemplos-software-diagramas-wysiwid.md` (sección 1-2)
   - Ver ejemplos de Kodless y repositorios reales

3. **Profundiza con**: `codigo-ejecutable-wysiwid.md` (sección 1-3)
   - Estudiar código real de conceptos

4. **Contexto académico**: `compass_artifact_wf-*.md`
   - Entender el paper y la investigación

### Si vas a implementar:
1. **Diseño**: `wysiwid-ejemplos-diagramas-mermaid.md` (sección 5, 10, 11)
   - Checklist de concepto válido
   - Mejores prácticas

2. **Código**: `codigo-ejecutable-wysiwid.md` (todo el documento)
   - Implementaciones completas con tests
   - Patrones de código

3. **Referencia**: `ejemplos-software-diagramas-wysiwid.md` (sección 5, 8.2)
   - Conceptos comunes reutilizables
   - Repositorios de código

### Si estás desarrollando con LLMs:
1. **Ventajas**: `wysiwid-ejemplos-diagramas-mermaid.md` (sección 6)
   - Por qué WYSIWID es LLM-friendly
   - Datos del estudio MIT (50% reducción en tiempo)

2. **Proceso**: `codigo-ejecutable-wysiwid.md` (sección 5.2)
   - Cómo generar conceptos con LLMs
   - Flujo de generación completa

3. **Prompts**: Ver carpeta `/prompts/` en la raíz del proyecto
   - concept_genie.txt
   - concept_spector.txt
   - route_genie.txt

---

## 🔗 Referencias Principales

### Paper y Publicaciones
- **Paper completo**: https://arxiv.org/abs/2508.14511
- **ACM Digital Library**: DOI 10.1145/3759429.3762628
- **Conferencia**: SPLASH Onward! 2024 (Octubre 2024)

### Repositorios de Código
- **Kodless**: https://github.com/kodless-org/kodless
- **Conception**: https://github.com/kodless-org/conception
- **Fritter (MIT 6.1040)**: https://github.com/61040-fa22/fritter-backend

### Recursos Educativos
- **Libro**: "The Essence of Software" - Daniel Jackson (Princeton Press, 2021)
- **Sitio web**: https://essenceofsoftware.com/
- **Blog WYSIWID**: https://essenceofsoftware.com/posts/wysiwid/
- **Curso MIT 6.1040**: https://61040-fa25.github.io/

### Videos y Charlas
- "Building an entire app with an LLM" (Jun 2024): https://www.youtube.com/watch?v=WgOhtH3lugk
- "What makes software work?" (May 2024): https://www.youtube.com/watch?v=pCr3GjdoTbg
- "A new modularity for software" (OOPSLA 2018): https://youtu.be/YoEkXHZ6Gbg

---

## 📊 Resumen Ejecutivo

**WYSIWID** es un patrón arquitectural que separa el software en:

1. **Concepts** - Módulos completamente independientes con estado y acciones propias
2. **Synchronizations** - Reglas declarativas que coordinan conceptos sin crear dependencias

### Ventajas Clave:
- ✅ **Modularidad radical**: Cero acoplamiento entre conceptos
- ✅ **LLM-friendly**: Generación incremental con contexto mínimo
- ✅ **Mantenibilidad**: Funcionalidad localizada, fácil de encontrar
- ✅ **Testabilidad**: Cada concepto se testea aisladamente
- ✅ **Reutilizabilidad**: Conceptos funcionan en múltiples contextos

### Implementado en Kodless:
Este repositorio (kodless) es el **prototipo original** que demostró el patrón WYSIWID en práctica, desarrollado por Barish Namazov en MIT y mencionado en la investigación académica.

---

## 🤝 Contribuciones

Esta documentación fue compilada en **Noviembre 2025** basada en:
- Paper académico WYSIWID (Splash Onward! 2024)
- Repositorios open-source de MIT
- Materiales del curso MIT 6.1040
- Charlas y presentaciones de Daniel Jackson
- Implementación práctica en Kodless

Para más información, consulta los documentos individuales o visita los enlaces de referencia.

---

**Última actualización**: Noviembre 2025
**Investigadores principales**: Daniel Jackson (MIT EECS), Eagon Meng (MIT CSAIL)
**Prototipo**: Barish Namazov (MIT '24)
