function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function get_map() {
    return new Promise((resolve) => {
        const iframeContent = document.querySelector('#memory_map').contentDocument;
        resolve(iframeContent.querySelector('iframe').contentDocument);
    })
}

async function init_map() {
    await sleep(100).then(async () => {
        await get_map().then((mapContent) => {
            // console.log(mapContent.body.innerHTML)
            mapContent.head.innerHTML = mapContent.head.innerHTML + '<style>.leaflet-popup {display: none}</style>';
        });
    })
        .catch(init_map)
}

function extract_coords(coords_str) {
    const key = '(\\w*)';
    const float = '([+-]?[0-9]*[.]?[0-9]+)';
    const re = new RegExp(`${key}: ${float}<br>${key}: ${float}`);

    const coords_arr = re.exec(coords_str).slice(1, 5);
    return {latitude: coords_arr[1], longitude: coords_arr[3]}
}

init_map().then(async () => {
    const observer = new MutationObserver(mutationRecords => {
        const coords_html = mutationRecords[0].target.querySelector('.leaflet-popup')
            .querySelector('.leaflet-popup-content').innerHTML;

        const coords = extract_coords(coords_html)
    });

    async function get_observer() {
        await sleep(100).then(async () => {
            await get_map().then((mapContent) => {

                console.log(mapContent.querySelector('.folium-map'))
                console.log(mapContent.querySelector('.leaflet-popup'))

                observer.observe(mapContent.querySelector('.leaflet-pane .leaflet-popup-pane'), {
                    childList: true,
                    attributes: false,
                    characterData: false,
                });
            });
        })
            .catch(get_observer)
    }

    await get_observer()
})



