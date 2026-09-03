(() => {
  "use strict";

  // Shapes and interactions follow Animate UI's open-source icon components:
  // https://github.com/imskyleen/animate-ui/tree/main/apps/www/registry/icons
  const icons = {
    "arrow-right":
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><g class="animate-icon__arrow"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></g></svg>',
    send: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><g class="animate-icon__send"><path d="M14.5,21.7c.1.3.4.4.7.3.1,0,.2-.2.3-.3L22,2.7c0-.3,0-.5-.3-.6-.1,0-.2,0-.3,0L2.3,8.5c-.3,0-.4.4-.3.6,0,.1.2.2.3.3l7.9,3.2c.5.2.9.6,1.1,1.1l3.2,7.9Z"/><path d="M21.9,2.1l-10.9,10.9"/></g></svg>',
    "external-link":
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><g class="animate-icon__external"><path d="M15 3h6v6"/><path d="M10 14 21 3"/></g><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/></svg>',
    heart:
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path class="animate-icon__heart" d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></svg>',
    menu: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line class="animate-icon__menu-line animate-icon__menu-line--top" x1="4" y1="6" x2="20" y2="6"/><line class="animate-icon__menu-line animate-icon__menu-line--middle" x1="4" y1="12" x2="20" y2="12"/><line class="animate-icon__menu-line animate-icon__menu-line--bottom" x1="4" y1="18" x2="20" y2="18"/></svg>',
  };

  document.querySelectorAll("[data-animate-icon]").forEach((node) => {
    node.innerHTML = icons[node.dataset.animateIcon] || "";
  });
})();
