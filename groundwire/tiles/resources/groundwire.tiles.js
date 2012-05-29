// jQuery function
/*global common_content_filter:false */
jQuery(function($) {
  $('div[data-tile], h1[data-tile], h2[data-tile]').each(function() {
      $(this).addClass('tile-editable');
      var href = $(this).attr('data-tile');
      var edithref = href.replace(/@@/, '@@edit-tile/');
      $('<a class="tile-edit-link" href="' + edithref + '"><img src="pencil_icon.png" width="16" height="16" alt="Edit Tile"/></a>')
        .appendTo($(this))
        .prepOverlay({
            subtype: 'iframe',
            config: {
              closeOnClick: false,
              mask: {
                color: '#000000',
                opacity: 0.8
              },
              onClose: function() {
                location.reload();
            }
            },
        });
  });
  
  // Check if tiledata is available and valid
  if (typeof(tiledata) !== 'undefined') {

      // Check action
      if (tiledata.action === 'cancel' || tiledata.action === 'save') {
          // Close dialog
          window.parent.jQuery('.link-overlay').each(function() {
              try {
                  window.parent.jQuery(this).overlay({api: true}).close();
              } catch(e) { }
          });
      }
  }
  $(document).bind('loadInsideOverlay', function() {
        $('textarea.mce_editable').each(function() {
          var id = $(this).attr('id'),
              config = new TinyMCEConfig(id);
          //var config = new TinyMCEConfig($(this).attr('id'));
          delete InitializedTinyMCEInstances[id];
          config.init();
        });
    });
  
});