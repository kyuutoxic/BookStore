from flask import redirect, request
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, expose, BaseView
from __init__ import app, db
from models import *
from flask_login import current_user, logout_user
import utils
from flask_admin import AdminIndexView


class ManagerView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and (current_user.role == UserRole.MANAGER or current_user.role == UserRole.ADMINISTRATOR)


class SellerView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and (current_user.role == UserRole.SELLER or current_user.role == UserRole.ADMINISTRATOR)


class StockkeeperView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and (current_user.role == UserRole.STOCKKEEPER or current_user.role == UserRole.ADMINISTRATOR)


class AdminView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == UserRole.ADMINISTRATOR


class AdminBaseView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == UserRole.ADMINISTRATOR


class EditView(AdminView):
    can_view_details = True
    edit_modal = True
    create_modal = True
    details_modal = True


class BookView(ManagerView):
    can_view_details = True
    edit_modal = True
    create_modal = True
    details_modal = True
    column_filters = ['name', 'price', 'category']
    form_excluded_columns = ['imports','receipt_details']
    column_exclude_list = ['image']


class UserView(EditView):
    form_excluded_columns = ['receipts']
    column_exclude_list = ['password', 'avatar']


class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html',
                           stats=utils.category_stats(), parent = utils.read_parentCategory())


class Imports(StockkeeperView):
    @expose('/')
    def index(self):
        err_msg = ''
        count = request.args.get('count')
        book_id = request.args.get('book')
        kw = request.args.get('kw')

        min_value = utils.get_rule(1)
        min_of_stock = utils.get_rule(2)


        book = utils.get_book(book_id)
        try:
            temp = book.quantity + int(count)
            if int(count) < min_value.value:
                err_msg = 'Value not enough!!!'
            elif book.quantity >= min_of_stock.value:               
                err_msg = 'Too many book in stock!!!'
            else:
                err_msg = 'Successful!!!'
                book.quantity = temp
                db.session.commit()
                utils.add_import(book_id = book.id, quantities = count)

        except Exception as ex:
            err_msg = ''
            
        return self.render('admin/import.html', book=utils.read_book(kw=kw),books=utils.read_book(), err_msg=err_msg, imports=utils.read_import())


class Sale(SellerView):
    @expose('/')
    def index(self):
        err_msg = ''
        id = request.args.get('id')
        cus_name = request.args.get('cus_name')

        if id:
            receipt = utils.add_receipt(user_id=id, cus_name=cus_name)

        kw = request.args.get('kw')

        book_id = request.args.get('book')
        quantity = request.args.get('quantity')
        receipt_id = request.args.get('receipt')


        if book_id and quantity and receipt_id:
            # p = utils.read_receiptdetails_by_receipt_id(receipt_id)
            # for i in p:
            #     if i.book_id==book_id:
            #         utils.update_quantity_receipt_details(receipt_detail_id=i.id, quantity=quantity)
            #         break
            # else:
            b = utils.get_book(book_id=book_id)
            if b.quantity >= int(quantity):
                utils.add_receiptdetails(receipt_id=receipt_id, book_id=book_id, quantity=quantity)
            else:
                err_msg = 'Quantity in stock is ' + str(b.quantity)


        receipt_detail = utils.read_receiptdetails_by_receipt_id(receipt_id=receipt_id)
        receipts = request.args.get('receipt')
        if receipts:
            receipt_detail = utils.read_receiptdetails_by_receipt_id(receipt_id=receipts)

        receipts_id = request.args.get('receipt_id')
        if receipts_id:
            receipt_detail_for_update_stock = utils.read_receiptdetails_by_receipt_id(receipt_id=receipts_id)
            for b in receipt_detail_for_update_stock:
                utils.update_stock(book_id=b.book_id, quantity=b.quantity)
            utils.update_receipt_status(receipts_id)

        book=utils.read_book(kw=kw)
        sum = 0
        for r in receipt_detail:
            for b in book:
                if b.id == r.book_id:
                    sum = sum + r.quantity * b.price

        
        receipt_detail_id = request.args.get('receipt_detail_id')
        if receipt_detail_id:
            utils.del_receipt_detail(receipt_detail_id=receipt_detail_id)


        return self.render('admin/invoice.html', book=book, err_msg=err_msg, receipts = utils.read_receipt_by_active(), 
                            receipt_detail=receipt_detail, get_receipt=utils.get_receipt_by_id(receipts), sum=sum)


class StatsView(AdminBaseView):
    @expose('/')
    def index(self):
        return self.render('admin/stats.html')


admin = Admin(app, name="Quản lý nhà sách",template_mode="bootstrap3", index_view=MyAdminIndexView())

admin.add_view(Imports(name='Import'))
admin.add_view(Sale(name='Sale'))
admin.add_view(UserView(User, db.session))
admin.add_view(BookView(Book, db.session))
# admin.add_view(ModelView(BookLanguage, db.session))
# admin.add_view(ModelView(Category, db.session))
# admin.add_view(ModelView(ParentCategory, db.session))
admin.add_view(EditView(Rule, db.session))
admin.add_view(StatsView(name='Stats'))
admin.add_view(LogoutView(name='Logout', menu_icon_type='fa', menu_icon_value='fa-connectdevelop'))

