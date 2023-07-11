//chapter edit
function edit() {
    $('.cancel, .save, .handle').show();
    $('.edit').hide();
};
function cancel() {
    $('.cancel, .save, .handle').hide();
    $('.edit').show();
    $('tbody').sortable('cancel');
}

//close menu
function closeMenu() {
    $('.content').attr('style', 'width: 100%');
    $('.close').attr('onclick', 'openMenu()');
};

//open menu
function openMenu() {
    $('.content').attr('style', 'width: calc(100% - 220px)');
    $('.close').attr('onclick', 'closeMenu()');
};

if (window.matchMedia("(max-width:1300px)").matches) {
    closeMenu()
} 

//menu
$('.menu-item').each(function() {
    var path = window.location.pathname
    var href = $(this).attr('href')
    if (path == href) {$(this).addClass('menu-selected')};
    if (path == '/start') {
        $('[href="/next"]').addClass('menu-selected')
    };
});

//language
function changeLanguage(current) {
    var path = window.location.pathname
    if (current == 'en') {
        var currentContent = location.pathname.split('/')
        currentContent[1] = 'pt-br';
    } else {
        var currentContent = location.pathname.split('/')
        currentContent[1] = 'en';
    }
        window.location.replace(currentContent.join('/'));
};

//problem search
$('#search').keyup(function() {
  var txt = $(this).val();
  $('.chapter').each(function() {
    if($(this).text().toUpperCase().indexOf(txt.toUpperCase()) != -1){
      $(this).show();
    } else {
      $(this).hide();
    }
  });
})

// chat
window.$zopim||(function(d,s){var z=$zopim=function(c){z._.push(c)},$=z.s=
    d.createElement(s),e=d.getElementsByTagName(s)[0];z.set=function(o){z.set.
_.push(o)};z._=[];z.set._=[];$.async=!0;$.setAttribute("charset","utf-8");
    $.src="https://v2.zopim.com/?64bHCyGA4wDlqZy77v5LXk9LOHCCnz9t";z.t=+new Date;$.
        type="text/javascript";e.parentNode.insertBefore($,e)})(document,"script");