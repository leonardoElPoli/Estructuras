from flask import render_template

def controladorSeccion(main):
    @main.route('/seccion1.html')
    def seccion1():
        return render_template('seccion1.html')
    
    @main.route('/seccion2.html')
    def seccion2():
        return render_template('seccion2.html')
    
    @main.route('/seccion3.html')
    def seccion3():
        return render_template('seccion3.html')
    
    @main.route('/seccion4.html')
    def seccion4():
        return render_template('seccion4.html')
    
    @main.route('/seccion5.html')
    def seccion5():
        return render_template('seccion5.html')

    @main.route('/seccion6.html')
    def seccion6():
        return render_template('seccion6.html')
    
    @main.route('/seccion7.html')
    def seccion7():
        return render_template('seccion7.html')
    
    @main.route('/seccion8.html')
    def seccion8():
        return render_template('seccion8.html')
    
    @main.route('/seccion9.html')
    def seccion9():
        return render_template('seccion9.html')

    @main.route('/seccion10.html')
    def seccion10():
        return render_template('seccion10.html')   