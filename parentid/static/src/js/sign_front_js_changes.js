odoo.define('parentid.sign_front_js_changes', function (require) {
    "use strict";
  
    var core = require('web.core');
    var config = require('web.config');
    var utils = require('web.utils');
    var Widget = require('web.Widget');
    var ajax = require('web.ajax');
    var qweb = core.qweb;
    var publicWidget = require('web.public.widget');
    var Dialog = require('web.Dialog');
    var session = require('web.session');
    var SignatureForm = require('portal.signature_form').SignatureForm;

    var NameAndSignature = require('web.name_and_signature').NameAndSignature;

    publicWidget.registry.SignatureForm = publicWidget.Widget.extend({
        selector: '.o_portal_signature_form',
    
        /**
         * @private
         */
        start: function () {
            var hasBeenReset = false;
       
            var callUrl = this.$el.data('call-url');
            var nameAndSignatureOptions = {
                defaultName: this.$el.data('default-name'),
                signerEmail:this.$el.data('default-email'),
                mode: this.$el.data('mode'),
                displaySignatureRatio: this.$el.data('signature-ratio'),
                signatureType: this.$el.data('signature-type'),
                fontColor: this.$el.data('font-color')  || 'black',
            };            
            if ($('#o_sign_input_email_address').val()!=undefined)
            {
                 this.signerEmail = $('#o_sign_input_email_address').val();}
            else
            {
               
            this.signerEmail=this.$el.data('default-email')
            }

            var sendLabel = this.$el.data('send-label');
    
            var form = new SignatureForm(this, {
                callUrl: callUrl,
                nameAndSignatureOptions: nameAndSignatureOptions,
                sendLabel: sendLabel,
            });
    
            // Correctly set up the signature area if it is inside a modal
            this.$el.closest('.modal').on('shown.bs.modal', function (ev) {
                if (!hasBeenReset) {
                    hasBeenReset = true;
                    form.resetSignature();
                } else {
                    form.focusName();
                }
            });
    
            return Promise.all([
                this._super.apply(this, arguments),
                form.appendTo(this.$el)
            ]);
        },
    });
    
        ajax.loadXML('/parentid/static/src/sign.xml', qweb);

})
   
