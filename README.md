# Entregable 3

## Integrantes:
- Daniela Arango
- David Grisales
- Juan Miguel Castro
- Camilo Cordoba

ALB URL Staging: http://calculadora-staging-alb-867266404.us-east-1.elb.amazonaws.com/
ALB URL Production: http://calculadora-production-alb-1719671958.us-east-1.elb.amazonaws.com/


### Explicación breve del nuevo workflow
El flujo implementado sigue una cadena controlada desde el commit hasta producción, donde el artefacto principal que se mueve es la imagen Docker versionada por el SHA del commit, garantizando trazabilidad entre código y despliegue. Todo inicia con un push a main, que dispara el pipeline de CI/CD.

En el job build-test-publish (CI) se valida la calidad del código y se construye el artefacto. Aquí se ejecutan linters (Black, Pylint, Flake8) para validar formato y estándares, pruebas unitarias con pytest para validar la lógica de negocio (funciones de la calculadora y endpoints Flask de forma aislada), y análisis estático con SonarCloud. Si el evento es un push a main, se construye y publica la imagen Docker en Docker Hub con dos tags: latest y el commit_sha. Este job produce como output el nombre del repositorio y el tag de la imagen, que serán consumidos en CD.

Luego, el job deploy-tf-staging toma ese artefacto (image URI) y ejecuta Terraform contra el entorno de staging. Inicializa el estado remoto en S3 y aplica la infraestructura pasando la nueva imagen como variable (docker_image_uri). Aquí Terraform actualiza la Task Definition de ECS y asegura que la infraestructura esté alineada con el código.

El job update-service-staging no cambia infraestructura, sino que fuerza un nuevo despliegue del servicio ECS para que consuma la nueva Task Definition con la imagen recién publicada. Espera hasta que el servicio esté estable, validando que el rollout a nivel de contenedores terminó correctamente.

Después, el job test-staging ejecuta pruebas de aceptación (end-to-end) usando Selenium contra la URL del ALB de staging. Estas pruebas validan el sistema completo desplegado: interfaz web, inputs del usuario, operaciones matemáticas y respuestas esperadas, incluyendo casos válidos y errores (división por cero, inputs inválidos). Aquí se asegura que la aplicación funciona correctamente en un entorno real.

Si staging pasa, se continúa con deploy-tf-prod, que replica el mismo proceso de Terraform pero contra producción, reutilizando exactamente la misma imagen (inmutabilidad del artefacto). Esto garantiza consistencia entre entornos.

Luego, update-service-prod fuerza el despliegue en ECS producción, asegurando que los nuevos contenedores con la imagen validada en staging entren en servicio y se estabilicen correctamente.

Finalmente, el job smoke-test-prod ejecuta pruebas de humo contra producción. Estas pruebas son mínimas y rápidas: verifican que la aplicación levanta, responde, y que elementos clave (como el título y estructura básica) están presentes. Su objetivo es detectar fallos críticos inmediatos post-deploy sin la complejidad de las pruebas de aceptación.

En conjunto, el flujo asegura: calidad de código (CI), despliegue reproducible (Terraform), promoción controlada entre entornos (staging → prod) y validación progresiva mediante pruebas unitarias, de aceptación y de humo.

### ¿Qué te pareció definir la infraestructura en HCL?
HCL nos pareció chévere porque es bastante legible, no es tan pesado como JSON ni tan complejo como otros lenguajes. Se siente como escribir configuración más que código, entonces es fácil de entender después de un rato.
Igual, tiene su curva de aprendizaje, sobre todo cuando empiezas con variables, módulos y referencias entre recursos. Ahí sí toca pensar un poquito más. Pero ya cuando le coges el tiro, se vuelve muy práctico.

### ¿Qué ventajas y desventajas tiene introducir un entorno de Staging en el pipeline de despliegue a AWS? ¿Cómo impacta esto la velocidad vs. la seguridad del despliegue?

Meter un staging es básicamente tener un “campo de pruebas” antes de producción, y eso es demasiado útil. Puedes probar cambios casi como si fuera producción sin romper nada importante. Eso mejora muchísimo la seguridad del despliegue, porque reduces el riesgo de subir algo roto.
Lo malo es que hace todo más lento, es decir, ya no es solo hacer deploy y listo, sino que pasa por staging, pruebas, validaciones. entonces el pipeline se vuelve más largo.
o sea que se ganas seguridad y confianza, pero sacrificas velocidad. Igual, en la vida real vale más no romper producción que ir rápido, entonces casi siempre compensa.

### ¿Qué diferencia hay entre las pruebas ejecutadas contra Staging (test-staging) y las ejecutadas contra Producción (smoke-test-production) en tu pipeline? ¿Por qué esta diferencia?

La diferencia clave está en profundidad, alcance y objetivo. En test-staging se ejecutan pruebas de aceptación end-to-end completas usando Selenium: simulan el comportamiento real del usuario (inputs, selección de operaciones, validación de resultados y manejo de errores). Estas pruebas validan la lógica funcional completa del sistema desplegado, incluyendo frontend, backend y su integración, con múltiples casos parametrizados. En cambio, en smoke-test-production se ejecuta un conjunto mínimo de verificaciones: carga de la aplicación, título, y elementos básicos del DOM. Su objetivo no es validar toda la funcionalidad, sino confirmar rápidamente que el sistema está vivo y respondiendo tras el despliegue. Esta diferencia existe porque staging es un entorno seguro para validar exhaustivamente sin impacto, mientras que en producción se prioriza rapidez, bajo costo y no intrusividad, evitando pruebas pesadas que puedan afectar usuarios reales o generar carga innecesaria.

### Considerando un ciclo completo de DevOps, ¿qué partes importantes (fases, herramientas, prácticas) crees que aún le faltan a este pipeline de CI/CD que has construido? (Menciona 2, explica por qué son importantes y cómo podrían implementarse brevemente).
Primero, observabilidad y monitoreo continuo. Actualmente el pipeline valida antes y justo después del deploy, pero no hay visibilidad operativa posterior. Esto es crítico para detectar degradaciones, errores en runtime o problemas de performance. Se podría implementar integrando métricas, logs y alertas con herramientas como CloudWatch (logs de ECS, métricas de ALB) y definir alarmas (latencia, tasa de errores 5xx). Además, agregar dashboards y alertas automáticas permitiría cerrar el ciclo de feedback.

Segundo, estrategias avanzadas de despliegue (deployment strategies) como rolling controlado, blue/green o canary. Actualmente se usa force-new-deployment, que reemplaza tareas pero sin validación progresiva del tráfico. Esto implica riesgo si una versión defectuosa llega a producción. Se podría mejorar usando despliegues blue/green con ALB (dos target groups) o canary releases, permitiendo enrutar tráfico gradualmente y validar métricas antes de completar el rollout, incluso automatizando rollback si se detectan fallos.

### ¿Cómo te pareció implementar dos funcionalidades nuevas? ¿Qué tal fue tu experiencia? ¿Encontraste útil implementar CI/CD a la hora de realizar cambios y despliegues? ¿Por qué? ¿Qué no fue tan útil?
Por un lado, el pipeline fue un dolor de cabeza al comienzo debido a los distintos errores que surgieron durante todo el pipeline relacionados con los nombres de las variables, de los repositorios y de los proyectos. Además de eso, ciertas restricciones entre SonarCloud y el despligue en AWS resultaron ser contradictorias (host=0.0.0.0 vs host=127.0.0.1).
Más sin embargo luego de implementado el pipeline, añadir las nuevas funciones permitía asegurarse que todo funcionaría correctamente, incluso después de tocar más de un archivo.