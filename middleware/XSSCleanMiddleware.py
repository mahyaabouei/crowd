# import bleach

# class XSSCleanMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         if request.method == 'POST':
#             for key, value in request.POST.items():
#                 request.POST[key] = bleach.clean(value)
#         response = self.get_response(request)
#         return response
