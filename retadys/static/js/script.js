$.fn.exists = function () {
    return this.length !== 0;
}
$(document).ready(function(){
    var timer;

    $(".move-up,.move-down,.move-left,.move-right").click(function(e){
        var row = $(this).parents("tr:first");

        //Con esto cancelamos el refresco automatico
        e.preventDefault();
        if (timer) {
            clearTimeout(timer);
            timer = null;
        }

        if ($(this).is(".move-up")) {
            //Mover 1 arriba
            $.ajax({url: "/aumentar-prioridad/" + row.attr('id'), type: "POST", success: function(result){
                if (result == "True") {
                    row.insertBefore(row.prev());
                }
            }});
        } else {
            if ($(this).is(".move-down")) {
                //Mover 1 abajo
                $.ajax({url: "/disminuir-prioridad/" + row.attr('id'), type: "POST", success: function(result){
                    if (result == "True") {
                        row.insertAfter(row.next());
                    }
                }});
            } else {
                if ($(this).is(".move-left")) {
                    //Mover 1 a la izquierda
                    var td = $(this).closest('table').parent().prev(); //Buscar el id de la maquina
                    if (td.exists()) {
                        $.ajax({
                            type: 'POST',
                            url: '/mover-a-maquina',
                            data: {
                                'idmaquina': td.attr('name'),
                                'idtarea': row.attr('id')
                            },
                            success: function(result){
                                if (result == "True") {
                                    refreshPage();
                                }
                            }
                        });
                    }
                } else {
                    if ($(this).is(".move-right")) {
                        //Mover 1 a la derecha
                        var td = $(this).closest('table').parent().next(); //Buscar el id de la maquina
                        td.css( "background", "#f99" );
                        if (td.exists()) {
                            $.ajax({
                                type: 'POST',
                                url: '/mover-a-maquina',
                                data: {
                                    'idmaquina': td.attr('name'),
                                    'idtarea': row.attr('id')
                                },
                                success: function(result){
                                    if (result == "True") {
                                        refreshPage();
                                    }
                                }
                            });
                        }
                    }
                }
            }
        }

        startTimer();
        return false;
    });

    $(".dissmiss").click(function(){
        $row = $(this).parents("tr:first");
        $.ajax({url: "/finalizar-tarea/" + $row.attr('id'), type: "POST", success: function(result){
            if (result === 'ok') {
                $row.remove();
            }
        }});
    });

    $(".add-job").click(function(){
        var codmaquina = $(this).children("span:first").html();
        $("#form-job").css({display: "inline"});
        $("#form-job-machinecod").html(codmaquina);
        $("#form-job-machine").val($(this).attr('id'));

        $jobs = $("select[name='form-job-work']");
        $("select[name='form-job-work'] option").remove(); //Quitar todas las entradas actuales
        $jobs.append('<option value=""></option>'); //La primera vacia
        $.getJSON("/maquinas/" + $(this).attr('id'), function(maquina){
            $.each(maquina.trabajos, function(i, trabajo){
                $jobs.append('<option value="' + maquina.trabajos[i].id + '">' + maquina.trabajos[i].orden_fabricacion + '</option>');
            });
        });


        return false;
    });

    $("#form-job-send").click(function(){
        $("#form-job").submit();
    });

    $("#form-job-cancel").click(function(){
        $("#form-job").css({display: "none"});
        return false;
    });

    function refreshPage() {
        location.reload();
    }

    function startTimer() {
        if (timer) {
          clearTimeout(timer);
          timer = null;
        }
        if (!disable_timer) {
            timer = setTimeout(refreshPage, 10000);
        }
    }

    //La pagina tiene refresco automatico cada 10 segundos
    startTimer();
});
