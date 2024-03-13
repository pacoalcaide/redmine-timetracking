# Readme.md

# Lista de tareas pendientes

- [ ]  la consulta de report entre fechas tiene los datos más a la vista para poder importar en Redmine
  - [ ]  quizás la duración esté más fácil en la consulta de los time entries (esta en segundos para poderla pasar a Redmine más fácil)
- [ ]  Generar ficheros de salida y de entrada
  - [ ] quedan como log y tb como backup de cada día de operación
  - [ ] cuando este preparado el fichero de Redmine se carga de una vez
- [ ]  lógica para trabajar los datos de Toogl para …
  - [ ]  "issue_id": <issue_id> OR "project_id": <project_id>
    - [ ]  si esta presente #99999 en Description hay ISSUE y sino, rellenar el proyecto
    - [ ]  sino hay ninguno, devolver error
  - [ ]  rellenar los “comments” de Redmine sacados del tratamiento de “description” en Toggl
- [ ]  datos constantes (…_id) que pueden estar guardados en el script para calcular
  - [ ]  proyecto_id
  - [ ]  activity_id
    - [ ]  sacarlo de TAGS de Toggl
  - [ ]  user_id ⇒ el de “alcaide” (user_id=3)
- [ ]  controlar si en Redmine si ya hay o no time entries en el día que se esta importanto desde Toggl
  - [ ]  no cargar esa info en ese caso
