from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from openid.consumer import consumer
from openid.extensions import ax, sreg
from socialregistration.clients import Client
from socialregistration.contrib.openid.storage import OpenIDStore
from socialregistration.settings import SESSION_KEY
import urlparse

AX_ATTRS = {
    'email': 'http://axschema.org/contact/email',
}

class OpenIDClient(Client):
    def __init__(self, session_data, endpoint_url, ax_attrs=None, sreg_attrs=None):
        self.endpoint_url = endpoint_url
        self.store = OpenIDStore()
        self.consumer = consumer.Consumer(session_data, self.store)
        self.ax_attrs = ax_attrs
        self.sreg_attrs = sreg_attrs
    
    def get_realm(self):
        if self.is_https():
            return 'https://%s/' % Site.objects.get_current().domain
        return 'http://%s/' % Site.objects.get_current().domain
    
    def get_callback_url(self, **kwargs):
        return urlparse.urljoin(self.get_realm(),
            reverse('socialregistration:openid:callback'))
    
    def get_redirect_url(self):
        auth_request = self.consumer.begin(self.endpoint_url)
        
        if self.ax_attrs:
            ax_request = ax.FetchRequest()
            for ax_attr in self.ax_attrs:
                ax_request.add(ax.AttrInfo(AX_ATTRS[ax_attr], required=True))
            auth_request.addExtension(ax_request)
        if self.sreg_attrs:
            auth_request.addExtension(sreg.SRegRequest(required=self.sreg_attrs))
        
        redirect_url = auth_request.redirectURL(self.get_realm(),
            self.get_callback_url())
        
        return redirect_url
    
    def complete(self, GET, path):
        self.result = self.consumer.complete(GET, urlparse.urljoin(self.get_realm(),
            path))
    
    def is_valid(self):
        return self.result.status == consumer.SUCCESS
    
    def get_identity(self):
        return self.result.identity_url
    
    def get_ax_result(self):
        if not self.ax_attrs:
            return {}
        
        if not hasattr(self, 'ax_result'):
            ax_response = ax.FetchResponse.fromSuccessResponse(self.result)
            print self.result
            if ax_response:
                self.ax_result = {ax_attr: ax_response.getSingle(AX_ATTRS[ax_attr], None)
                                 for ax_attr in self.ax_attrs}
            else:
                return {}
        
        return self.ax_result
    
    def get_sreg_result(self):
        if not self.sreg_attrs:
            return {}

        if not hasattr(self, 'sreg_result'):
            self.sreg_result = sreg.SRegResponse.fromSuccessResponse(self.result) or {}
        
        return self.sreg_result
    
    @staticmethod
    def get_session_key():
        return '%sopenid' % SESSION_KEY
