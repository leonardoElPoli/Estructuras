from flask import render_template

def controladorReporte(main, generar_reporte_ingreso):
    @main.route('/generar_reporte')
    def generar_reporte():
        return render_template('reporte.html', data= generar_reporte_ingreso())
    
    @main.route('/logoSecciones.html')
    def logoSecciones():
        return render_template('logoSecciones.html')
    
    

    
