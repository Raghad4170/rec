odoo.define('parentid.sign_back_changes', function(require) {
    'use strict';
        var core = require('web.core');
        var config = require('web.config');
        var utils = require('web.utils');
        var Widget = require('web.Widget');
        // var Widget = require('web.name_and_signature');
        var ajax = require('web.ajax');
        var qweb = core.qweb;
        var QWeb = core.qweb;

        var Dialog = require('web.Dialog');
        var session = require('web.session');
        var NameAndSignature = require('web.name_and_signature').NameAndSignature;
        var publicWidget = require('web.public.widget');
        var SignatureForm= require('portal.signature_form').SignatureForm

        NameAndSignature.include({



            events: _.extend({}, NameAndSignature.prototype.events, {
                'click .sign_two_clear': '_onClickSignDrawCleartwo',
            }),

          

                /**
     * Handles click on clear: empties the signature field.
     *
     * @see mode 'draw'
     * @private
     * @param {Event} ev
     */
        _onClickSignDrawCleartwo: function (ev) {
        ev.preventDefault();
        this.$signatureFieldtwo.jSignature('reset');
    },

        })

        SignatureForm.include({





                //----------------------------------------------------------------------
    // Handlers
    //----------------------------------------------------------------------

    /**
     * Handles click on the submit button.
     *
     * This will get the current name and signature and validate them.
     * If they are valid, they are sent to the server, and the reponse is
     * handled. If they are invalid, it will display the errors to the user.
     *
     * @private
     * @param {Event} ev
     * @returns {Deferred}
     */
    _onClickSignSubmit: function (ev) {
        var self = this;
        ev.preventDefault();

        if (!this.nameAndSignature.validateSignature()) {
            return;
        }

        var name = this.nameAndSignature.getName();
        var signature = this.nameAndSignature.getSignatureImage()[1];
        var sign_name = this.nameAndSignature.getSignatureImagetwo()[1];

        return this._rpc({
            route: this.callUrl,
            params: _.extend(this.rpcParams, {
                'name': name,
                'signature': signature,
                'sign_name':sign_name
            }),
        }).then(function (data) {
            if (data.error) {
                self.$('.o_portal_sign_error_msg').remove();
                self.$controls.prepend(qweb.render('portal.portal_signature_error', {widget: data}));
            } else if (data.success) {
                var $success = qweb.render('portal.portal_signature_success', {widget: data});
                self.$el.empty().append($success);
            }
            if (data.force_refresh) {
                if (data.redirect_url) {
                    window.location = data.redirect_url;
                } else {
                    window.location.reload();
                }
                // no resolve if we reload the page
                return new Promise(function () { });
            }
        });
    },


        }),

        Widget.include({




            willStart: function () {
                var self = this;
                this.size = 'medium'; 
                // alert($('#sale_order').val())
                console.log($('#o_sign_input_email_address').val())
                if ($('#sale_order').val()!=undefined)
                {

                    // alert("yeeeeeeeeeeeeeeeeeeeeeeeeer")
                    this.sale_order=true
                }
                if ($('#o_sign_input_email_address').val()!=undefined)
                {
                     this.signerEmail = $('#o_sign_input_email_address').val();}
               
                return Promise.all([
                    this._super.apply(this, arguments)
                    // this._rpc({route: '/web/sign/get_fonts/' + self.defaultFont}).then(function (data) {
                    //     self.fonts = data;
                    // })
                ]);
            },


              /**
     * Finds the DOM elements, initializes the signature area,
     * and focus the name field.
     *
     * @override
     */
    start: function () {
        var self = this;

        this.$signatureFieldtwo = this.$('.o_web_sign_signature_two');


        return this._super.apply(this, arguments);
    },

    getSignatureImagetwo: function () {
        return this.$signatureFieldtwo.jSignature('getData', 'image');
    },
    /**
     * Gets the signature currently drawn, in a format ready to be used in
     * an <img/> src attribute.
     *
     * @returns {string} the signature currently drawn, src ready
     */
    getSignatureImageSrctwo: function () {
        return this.$signatureFieldtwo.jSignature('getData');
    },
 
        });

        // NameAndSignature.include({

        //     events: _.extend({
        //         "click .o_send_email":  _.debounce(function() {
        //             this._sendemails();
        //         }, 200, true),
        //         "click .make_visible":  _.debounce(function() {
        //            this._reload()
        //         }, 200, true),
        //         "click .o_send_email_verify":  _.debounce(function() {
        //             this._verifycode();
        //         }, 200, true),
        //     }, NameAndSignature.prototype.events),
       
            
        //     _reload: function() {
        //         if($('.make_visible').prop('checked')) {
        //             var targList = document.getElementsByClassName("o_web_sign_signature_group");
          
        //             if (targList) {
        //                 for (var x = 0; x < targList.length; x++) {
        //                   targList[x].style.visibility = "visible";

        //                 }
        //             }
                
        //           ;
        //         } else {
        //             alert("Checked Box deselect");
        //         }

        //     },

        //     _sendemails: function() {
        //         var self = this;
        //         return self._rpc({
        //             route: '/send_verification_mail',
        //             params: {
        //                 email:this.$(".o_sign_email_input").val()
        //             },
        //         }).then(function (demo_active) {
        //             // self.demo_active = demo_active;
        //         });

               
               
        //     },
        //     _verifycode: function() {
        //         var self = this;
        //         return self._rpc({
        //             route: '/confirm_code',
        //             params: {
        //                 vcode:this.$(".validation_code_email").val()

        //             },
        //         }).then(function (result) {
        //             if (result==true)
        //             {
        //                 var targList = document.getElementsByClassName("o_web_sign_signature_group");
          
        //                 if (targList) {
        //                     for (var x = 0; x < targList.length; x++) {
        //                       targList[x].style.visibility = "visible";
    
        //                     }
        //                 }
                        
        //             }
        //             if (result==false)
        //             {
        //                 alert("Wrong Code,Please Enter correct code from sent Email!!!")
        //             }

        //         });             
        //     },

        //     willStart: function () {
        //         var self = this;
        //         this.size = 'medium'; 
        //         alert("llllllllllllllllllllllllldjdjdjd")
        //         return Promise.all([
        //             this._super.apply(this, arguments),
        //             this._rpc({route: '/web/sign/get_fonts/' + self.defaultFont}).then(function (data) {
        //                 self.fonts = data;
        //             })
        //         ]);
        //     },
      
        // });
        // ajax.loadXML('/parentid/static/src/sign.xml', qweb);

    })
       
