# Casos esperados

`evaluation_cases.json` contiene 33 casos puros de entrada, configuración y resultado esperado. CP-12 se conserva en `integration_cases.json` porque necesita persistencia real. Los CP-01 a CP-11 corresponden a la matriz inicial de F1; el resto amplía el contrato.

El campo `confirmar_todas` modela el estado posterior a una revisión explícita para probar el motor. **No es una bandera aceptada por la API para saltarse confirmaciones**: la API necesita token y claves de coincidencias. En fixtures se comparan estados, numerador, denominador, porcentaje a un decimal y coincidencias por tipo/campo. Para `esperado.error`, comprobar el código de validación y ausencia de evaluación persistida.

En casos sin `desafio_codigo` usar su `configuracion_propia` con las reglas C1–C6. El objetivo se prueba además en INT-05/AT-07. Los ejemplos no incluyen contraseñas ni cuentas para que las pruebas creen sus propios usuarios aislados.

CP-25 documenta que texto breve presente no equivale a calidad. CP-27/28 conservan falsos negativos conocidos para exponer el límite de los patrones, no para considerarlos seguros. Toda modificación del detector requiere revisar también estos casos y explicar el cambio.

Los archivos son un corpus preparado. La implementación debe ejecutar pruebas reales y registrar resultados sin reemplazar las expectativas por la salida del motor.
