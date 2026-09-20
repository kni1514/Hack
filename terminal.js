(function() {
    const terminal = document.querySelector('colab-xterm-terminal');

    if (!terminal) {
        console.error('Niranjan open Terminal !');
        return;
    }

    const style = document.createElement('style');

    style.innerHTML = `
        .fullscreen-terminal-mode {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            z-index: 999999 !important;
            background: #000000 !important;
        }

        body {
            overflow: hidden !important;
        }
    `;

    document.head.appendChild(style);

    terminal.classList.add('fullscreen-terminal-mode');
    terminal.style.backgroundColor = '#000000';

    if (terminal.shadowRoot) {
        const xtermScreen = terminal.shadowRoot.querySelector('.xterm-screen');
        const xtermViewport = terminal.shadowRoot.querySelector('.xterm-viewport');

        if (xtermScreen) {
            xtermScreen.style.backgroundColor = '#000000';
        }

        if (xtermViewport) {
            xtermViewport.style.backgroundColor = '#000000';
        }
    }

    window.dispatchEvent(new Event('resize'));

    console.log('All Done Niranjan !\nPlease Enjoy Hacking !');
})();
