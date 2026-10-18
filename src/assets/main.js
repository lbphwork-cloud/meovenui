(function () {
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  // Menu trên điện thoại
  var toggle = $('.nav-toggle'), nav = $('.nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open);
      toggle.textContent = open ? 'Đóng' : 'Menu';
    });
    $$('a', nav).forEach(function (a) { a.addEventListener('click', function () { nav.classList.remove('open'); toggle.textContent = 'Menu'; }); });
  }

  // Thông báo nhỏ
  var toast = $('.toast');
  function say(msg) {
    if (!toast) return;
    toast.textContent = msg; toast.classList.add('show');
    clearTimeout(say.t); say.t = setTimeout(function () { toast.classList.remove('show'); }, 3200);
  }
  function copy(text) {
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(text);
    return new Promise(function (ok, fail) {
      var t = document.createElement('textarea'); t.value = text; t.style.position = 'fixed'; t.style.opacity = '0';
      document.body.appendChild(t); t.select();
      try { document.execCommand('copy') ? ok() : fail(); } catch (e) { fail(e); }
      document.body.removeChild(t);
    });
  }

  // Video TikTok mở trong cửa sổ nổi, chỉ tải khi bấm
  var vm = $('#video-modal');
  function closeModal(m) {
    m.classList.remove('open'); document.body.style.overflow = '';
    var f = $('iframe', m); if (f) f.src = 'about:blank';
  }
  $$('[data-video]').forEach(function (b) {
    b.addEventListener('click', function () {
      var id = b.getAttribute('data-video');
      $('iframe', vm).src = 'https://www.tiktok.com/player/v1/' + id + '?autoplay=1&rel=0&description=1&music_info=0';
      $('.modal__link', vm).href = 'https://www.tiktok.com/@meovenui/video/' + id;
      vm.classList.add('open'); document.body.style.overflow = 'hidden';
    });
  });

  // Phóng to ảnh
  var lb = $('#lightbox');
  $$('[data-zoom]').forEach(function (img) {
    img.addEventListener('click', function () {
      var big = $('img', lb);
      big.src = img.getAttribute('data-zoom'); big.alt = img.alt || '';
      lb.classList.add('open'); document.body.style.overflow = 'hidden';
    });
  });

  $$('.modal').forEach(function (m) {
    m.addEventListener('click', function (e) { if (e.target === m || e.target.closest('.modal__close')) closeModal(m); });
  });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') $$('.modal.open').forEach(closeModal); });

  // Đặt tour qua Zalo: copy sẵn câu hỏi rồi mở Zalo
  $$('[data-book]').forEach(function (a) {
    a.addEventListener('click', function () {
      var msg = a.getAttribute('data-book');
      copy(msg).then(function () { say('Đã copy sẵn tin nhắn rồi nè, bạn dán vào Zalo cho Mèo nha'); }, function () {});
    });
  });

  // Copy link tour để gửi khách
  $$('[data-copy-link]').forEach(function (b) {
    b.addEventListener('click', function () {
      var url = b.getAttribute('data-copy-link') || location.href;
      if (navigator.share && /Mobi|Android/i.test(navigator.userAgent)) {
        navigator.share({ title: document.title, url: url }).catch(function () {});
        return;
      }
      copy(url).then(function () { say('Đã copy link tour rồi nha'); }, function () { say(url); });
    });
  });

  // Đánh dấu mục đang xem trên thanh mục lục
  var sublinks = $$('.subnav a');
  if (sublinks.length && 'IntersectionObserver' in window) {
    var map = {};
    sublinks.forEach(function (a) { map[a.getAttribute('href').slice(1)] = a; });
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting) {
          sublinks.forEach(function (a) { a.classList.remove('active'); });
          var a = map[e.target.id]; if (a) { a.classList.add('active'); a.scrollIntoView({ block: 'nearest', inline: 'center', behavior: 'smooth' }); }
        }
      });
    }, { rootMargin: '-40% 0px -55% 0px' });
    Object.keys(map).forEach(function (id) { var el = document.getElementById(id); if (el) io.observe(el); });
  }

  // Hiện dần khi cuộn
  if ('IntersectionObserver' in window) {
    var ro = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); ro.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    $$('.reveal').forEach(function (el) { ro.observe(el); });
  } else {
    $$('.reveal').forEach(function (el) { el.classList.add('in'); });
  }
})();
