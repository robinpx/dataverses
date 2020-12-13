function get_image() {
    const xmlhttp = new XMLHttpRequest();
    xmlhttp.open('GET', '/image', true);
    xmlhttp.onreadystatechange = function() {
        if (xmlhttp.readyState == 4) {
            if (xmlhttp.status == 200) {
                let obj = JSON.parse(xmlhttp.responseText);
                load_info(obj);
            }
            else {
                error();
            }
        }
    };
    xmlhttp.send(null);
}

function load_info(object) {
    create_source(object);
    create_poem(object);
    create_hist(object);
}

function create_source(object) { 
    const title = document.getElementById('left-title');
    let link = document.createElement('a')
    link.href = object['url']
    link.target = '_'
    link.innerHTML = 'source &mdash; cooper hewitt'
    title.innerHTML = '';
    title.appendChild(link);
    title.className = '';
    const img = document.createElement('img');
    img.src = object['img'];
    document.getElementsByTagName('footer')[0].style.display = 'block';
    document.getElementById('left-block').appendChild(img);
}

function create_poem(object) {
    let poem_contents = object['poem'].replaceAll('\n', '<br>');
    poem_contents = poem_contents.replaceAll(' ','&nbsp;');
    const poem = document.createElement('p');
    const poemwrapper = document.createElement('div')
    const name = document.createElement('h2');
    name.innerHTML = object['name'] + '<br>' + object['artist'];
    poem.innerHTML = poem_contents;
    document.getElementById('top-block').appendChild(name);
    poemwrapper.appendChild(poem);
    document.getElementById('right-block').appendChild(poemwrapper);
}

function create_hist(object) {
    let blocks = document.getElementsByClassName('hist-block');
    let totalled = 0;
    for (let i=0; i < blocks.length;i++) {
        let colors = object['top_colors'];
        let rgb = colors[i*3] +',' + colors[(i*3)+1] + ',' + colors[(i*3)+2];
        let freq = object['frequencies'];
        if (i !== blocks.length - 1) {
            let wid = parseFloat(freq[i]) * 100;
            wid = parseInt(wid);
            totalled += wid;
            blocks[i].setAttribute('style','background:rgb(' + rgb + ');width:' + wid + '%;');
        }
        else {
            let diff = 100 - totalled;
            blocks[i].setAttribute('style','background:rgb(' + rgb + ');width:' + diff + '%;');
        }

    }
}

function error() {
    document.getElementById('left-title').innerHTML = 'there was an error... reload?';
}

get_image()