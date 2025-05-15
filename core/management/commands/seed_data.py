from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
import random
from faker import Faker

from stories.models import Tag, Story, Comment
from blogs.models import Blog, BlogComment
from forums.models import ForumCategory, ForumThread, ForumPost
from centers.models import DialysisCenter
from products.models import ProductCategory, Product, ProductReview, Cart, CartItem, Wishlist, Order, OrderItem
from feedback.models import Feedback, FeedbackResponse

User = get_user_model()
fake = Faker('en_IN')  # Using Indian locale

class Command(BaseCommand):
    help = 'Seeds the database with sample data'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')
        
        self.create_users()
        self.create_tags()
        self.create_stories()
        self.create_blogs()
        self.create_forum_categories()
        self.create_forum_threads()
        self.create_dialysis_centers()
        self.create_product_categories()
        self.create_products()
        self.create_carts_and_wishlists()
        self.create_orders()
        self.create_feedback()
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded database'))

    def create_users(self):
        self.stdout.write('Creating users...')
        
        # Create admin user
        admin, created = User.objects.get_or_create(
            email='admin@ourkidneystory.com',
            defaults={
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'ADMIN',
                'is_staff': True,
                'is_superuser': True,
                'city': 'Mumbai'
            }
        )
        
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(f'Created admin user: {admin.email}')
        
        # Create regular users
        roles = ['PATIENT', 'CAREGIVER']
        cities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 'Pune']
        
        for i in range(20):
            role = random.choice(roles)
            city = random.choice(cities)
            
            user, created = User.objects.get_or_create(
                email=fake.email(),
                defaults={
                    'first_name': fake.first_name(),
                    'last_name': fake.last_name(),
                    'role': role,
                    'city': city,
                    'avatar_url': f"https://i.pravatar.cc/150?img={i+1}"
                }
            )
            
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'Created user: {user.email}')

    def create_tags(self):
        self.stdout.write('Creating tags...')
        
        tags = [
            'dialysis', 'transplant', 'diet', 'medication', 'exercise',
            'mental health', 'support', 'caregiving', 'treatment',
            'research', 'lifestyle', 'nutrition', 'wellness', 'community'
        ]
        
        for tag_name in tags:
            Tag.objects.get_or_create(name=tag_name)
            
        self.stdout.write(f'Created {len(tags)} tags')

    def create_stories(self):
        self.stdout.write('Creating stories...')
        
        users = User.objects.all()
        tags = Tag.objects.all()
        
        for i in range(30):
            user = random.choice(users)
            title = fake.sentence()
            body = '\n\n'.join(fake.paragraphs(nb=5))
            
            story = Story.objects.create(
                title=title,
                body=body,
                user=user,
                image_url=f"https://picsum.photos/seed/story{i}/800/400"
            )
            
            # Add random tags
            story_tags = random.sample(list(tags), random.randint(1, 5))
            story.tags.set(story_tags)
            
            # Add random likes
            likers = random.sample(list(users), random.randint(0, 10))
            story.likes.set(likers)
            
            # Add random views
            story.views = random.randint(10, 200)
            story.save()
            
            # Add comments
            for _ in range(random.randint(0, 5)):
                commenter = random.choice(users)
                comment = Comment.objects.create(
                    story=story,
                    user=commenter,
                    content=fake.paragraph()
                )
                
                # Add replies to some comments
                if random.random() > 0.7:
                    for _ in range(random.randint(1, 3)):
                        replier = random.choice(users)
                        Comment.objects.create(
                            story=story,
                            user=replier,
                            content=fake.paragraph(),
                            parent=comment
                        )
        
        self.stdout.write(f'Created 30 stories with comments')

    def create_blogs(self):
        self.stdout.write('Creating blogs...')
        
        admin_users = User.objects.filter(role='ADMIN')
        tags = Tag.objects.all()
        
        for i in range(15):
            author = random.choice(admin_users)
            title = fake.sentence()
            content = '\n\n'.join(fake.paragraphs(nb=8))
            
            blog = Blog.objects.create(
                title=title,
                content=content,
                author=author,
                thumbnail_url=f"https://picsum.photos/seed/blog{i}/800/400",
                published=random.random() > 0.2
            )
            
            # Add random tags
            blog_tags = random.sample(list(tags), random.randint(1, 5))
            blog.tags.set(blog_tags)
            
            # Add random views
            blog.views = random.randint(20, 500)
            blog.save()
            
            # Add comments
            users = User.objects.all()
            for _ in range(random.randint(0, 8)):
                commenter = random.choice(users)
                comment = BlogComment.objects.create(
                    blog=blog,
                    user=commenter,
                    content=fake.paragraph()
                )
                
                # Add replies to some comments
                if random.random() > 0.7:
                    for _ in range(random.randint(1, 2)):
                        replier = random.choice(users)
                        BlogComment.objects.create(
                            blog=blog,
                            user=replier,
                            content=fake.paragraph(),
                            parent=comment
                        )
        
        self.stdout.write(f'Created 15 blogs with comments')

    def create_forum_categories(self):
        self.stdout.write('Creating forum categories...')
        
        categories = [
            {'name': 'General Discussion', 'description': 'General topics related to kidney health and community.'},
            {'name': 'Dialysis', 'description': 'Discussions about dialysis treatments, experiences, and tips.'},
            {'name': 'Diet & Nutrition', 'description': 'Share kidney-friendly recipes and dietary advice.'},
            {'name': 'Mental Health', 'description': 'Support for mental health challenges related to kidney disease.'},
            {'name': 'Caregivers Corner', 'description': 'A space for caregivers to share experiences and advice.'},
            {'name': 'Treatment Options', 'description': 'Discuss various treatment options and experiences.'},
            {'name': 'Transplant', 'description': 'Information and experiences about kidney transplants.'},
        ]
        
        for category_data in categories:
            ForumCategory.objects.get_or_create(
                name=category_data['name'],
                defaults={'description': category_data['description']}
            )
            
        self.stdout.write(f'Created {len(categories)} forum categories')

    def create_forum_threads(self):
        self.stdout.write('Creating forum threads and posts...')
        
        users = User.objects.all()
        categories = ForumCategory.objects.all()
        
        for i in range(40):
            user = random.choice(users)
            category = random.choice(categories)
            title = fake.sentence()
            
            thread = ForumThread.objects.create(
                title=title,
                category=category,
                user=user,
                is_pinned=random.random() > 0.9,
                is_closed=random.random() > 0.9,
                views=random.randint(5, 100)
            )
            
            # Create first post (thread content)
            first_post = ForumPost.objects.create(
                thread=thread,
                user=user,
                content='\n\n'.join(fake.paragraphs(nb=2))
            )
            
            # Add replies
            for _ in range(random.randint(0, 10)):
                replier = random.choice(users)
                post = ForumPost.objects.create(
                    thread=thread,
                    user=replier,
                    content=fake.paragraph()
                )
                
                # Add nested replies to some posts
                if random.random() > 0.7:
                    for _ in range(random.randint(1, 3)):
                        nested_replier = random.choice(users)
                        ForumPost.objects.create(
                            thread=thread,
                            user=nested_replier,
                            content=fake.paragraph(),
                            parent=post
                        )
        
        self.stdout.write(f'Created 40 forum threads with posts')

    def create_dialysis_centers(self):
        self.stdout.write('Creating dialysis centers...')
        
        cities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 'Pune', 
                 'Ahmedabad', 'Jaipur', 'Lucknow', 'Kochi', 'Chandigarh']
        
        center_types = ['HOSPITAL', 'STANDALONE']
        
        for i in range(30):
            city = random.choice(cities)
            center_type = random.choice(center_types)
            
            DialysisCenter.objects.create(
                name=f"{fake.company()} {center_type.title()} Dialysis Center",
                address=fake.address(),
                city=city,
                state=fake.state(),
                contact=fake.phone_number(),
                email=fake.company_email(),
                website=fake.url(),
                type=center_type,
                description=fake.paragraph(),
                image_url=f"https://picsum.photos/seed/center{i}/800/400",
                latitude=float(fake.latitude()),
                longitude=float(fake.longitude())
            )
            
        self.stdout.write(f'Created 30 dialysis centers')

    def create_product_categories(self):
        self.stdout.write('Creating product categories...')
        
        categories = [
            {'name': 'Dietary Supplements', 'description': 'Supplements designed for kidney patients.'},
            {'name': 'Medical Devices', 'description': 'Devices to help monitor health at home.'},
            {'name': 'Books & Education', 'description': 'Educational resources about kidney health.'},
            {'name': 'Comfort Items', 'description': 'Items to improve comfort during dialysis and recovery.'},
            {'name': 'Kidney-Friendly Foods', 'description': 'Foods specially formulated for kidney patients.'},
            {'name': 'Medication Organizers', 'description': 'Tools to help manage medications.'},
            {'name': 'Fitness & Wellness', 'description': 'Products to support physical activity and wellness.'},
        ]
        
        for category_data in categories:
            ProductCategory.objects.get_or_create(
                name=category_data['name'],
                defaults={'description': category_data['description']}
            )
            
        self.stdout.write(f'Created {len(categories)} product categories')

    def create_products(self):
        self.stdout.write('Creating products...')
        
        categories = ProductCategory.objects.all()
        tags = Tag.objects.all()
        users = User.objects.all()
        
        for i in range(50):
            category = random.choice(categories)
            title = fake.catch_phrase()
            description = fake.paragraph(nb_sentences=5)
            price = round(random.uniform(99, 9999), 2)
            
            product = Product.objects.create(
                title=title,
                description=description,
                image_url=f"https://picsum.photos/seed/product{i}/800/800",
                category=category,
                price=price,
                in_stock=random.random() > 0.1
            )
            
            # Add random tags
            product_tags = random.sample(list(tags), random.randint(1, 3))
            product.tags.set(product_tags)
            
            # Add reviews
            for _ in range(random.randint(0, 8)):
                reviewer = random.choice(users)
                
                # Skip if user already reviewed this product
                if not ProductReview.objects.filter(product=product, user=reviewer).exists():
                    ProductReview.objects.create(
                        product=product,
                        user=reviewer,
                        rating=random.randint(1, 5),
                        comment=fake.paragraph()
                    )
            
        self.stdout.write(f'Created 50 products with reviews')

    def create_carts_and_wishlists(self):
        self.stdout.write('Creating carts and wishlists...')
        
        users = User.objects.filter(role__in=['PATIENT', 'CAREGIVER'])
        products = Product.objects.all()
        
        for user in users:
            # Create cart
            cart, _ = Cart.objects.get_or_create(user=user)
            
            # Add random items to cart
            cart_products = random.sample(list(products), random.randint(0, 5))
            for product in cart_products:
                CartItem.objects.create(
                    cart=cart,
                    product=product,
                    quantity=random.randint(1, 3)
                )
            
            # Create wishlist
            wishlist, _ = Wishlist.objects.get_or_create(user=user)
            
            # Add random products to wishlist
            wishlist_products = random.sample(list(products), random.randint(0, 8))
            wishlist.products.set(wishlist_products)
            
        self.stdout.write(f'Created carts and wishlists for {users.count()} users')

    def create_orders(self):
        self.stdout.write('Creating orders...')
        
        users = User.objects.filter(role__in=['PATIENT', 'CAREGIVER'])
        products = Product.objects.all()
        statuses = ['PENDING', 'SHIPPED', 'DELIVERED', 'CANCELLED']
        
        for _ in range(30):
            user = random.choice(users)
            status = random.choice(statuses)
            
            # Create order
            order_products = random.sample(list(products), random.randint(1, 5))
            total_amount = 0
            
            order = Order.objects.create(
                user=user,
                status=status,
                shipping_address=fake.address(),
                contact_number=fake.phone_number(),
                total_amount=0  # Will update after adding items
            )
            
            # Add order items
            for product in order_products:
                quantity = random.randint(1, 3)
                price = product.price
                total_amount += price * quantity
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=price
                )
            
            # Update total amount
            order.total_amount = total_amount
            order.save()
            
        self.stdout.write(f'Created 30 orders')

    def create_feedback(self):
        self.stdout.write('Creating feedback...')
        
        users = User.objects.all()
        admin_users = User.objects.filter(role='ADMIN')
        feedback_types = ['BUG', 'FEATURE', 'GENERAL']
        statuses = ['PENDING', 'ACCEPTED', 'DECLINED', 'IMPLEMENTED']
        
        for i in range(20):
            user = random.choice(users)
            feedback_type = random.choice(feedback_types)
            status = random.choice(statuses)
            
            feedback = Feedback.objects.create(
                title=fake.sentence(),
                description=fake.paragraph(nb_sentences=3),
                type=feedback_type,
                status=status,
                user=user
            )
            
            # Add responses for some feedback
            if random.random() > 0.3:
                admin = random.choice(admin_users)
                FeedbackResponse.objects.create(
                    feedback=feedback,
                    user=admin,
                    content=fake.paragraph()
                )
                
                # Sometimes add a reply from the user
                if random.random() > 0.5:
                    FeedbackResponse.objects.create(
                        feedback=feedback,
                        user=user,
                        content=fake.paragraph()
                    )
            
        self.stdout.write(f'Created 20 feedback items with responses')
