window.onload = function () {
    let $picker = document.getElementById("colorPicker"), picker = tinycolorpicker($picker);
    let ws = new WebSocket("ws://192.168.4.1:80");

    ws.onmessage = function (evt) {

        document.getElementById("response").innerHTML = evt.data;
        let resp = JSON.parse(evt.data);

        if (typeof (resp.rgb) !== 'undefined') {

            document.getElementsByClassName('colorInner')[0].style.background = 'rgb(' + [resp.rgb.r, resp.rgb.g, resp.rgb.b].join(',') + ')';

            let battery = document.getElementsByClassName('battery-level')[0];
            battery.style.height = resp.percentage + '%';
            if (resp.percentage <= 10) {
                battery.classList.add('alert');
                battery.classList.remove('warn');
            } else if (resp.percentage <= 30) {
                battery.classList.add('warn');
                battery.classList.remove('alert');
            } else {
                battery.classList.remove('warn');
                battery.classList.remove('alert');
            }
        }

    };

    $picker.addEventListener('change', function (e) {
        ws.send(JSON.stringify({
            command: "color",
            hex_color: e.target.querySelector('.colorInput').value,
            intensity: parseInt(document.querySelector('input[name="intensity"]').value)
        }))
    }, false);

    Array.prototype.forEach.call(document.getElementsByClassName("command"), function (element) {
        element.addEventListener('click', function (e) {
            e.preventDefault();

            let action = element.getAttribute('data-action');
            let payload = {command: action};

            if (!['cancel', 'status'].includes(action)) {
                payload['intensity'] = parseInt(document.querySelector('input[name="intensity"]').value);
            }

            if (action === 'fade') {
                payload['period'] = parseFloat(document.querySelector('input[name="period"]').value);
            } else if (action === 'jump') {
                payload['mode'] = parseInt(document.querySelector('input[name="mode"]:checked').value);
                payload['speed'] = parseFloat(document.querySelector('input[name="speed"]').value);
            }

            ws.send(JSON.stringify(payload));

        }, false);
    })
};
