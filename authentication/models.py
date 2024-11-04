from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError

def validate_file_type(file):
    valid_mime_types = [
        'image/jpeg', 'image/png', 'application/pdf',
        'application/zip', 'application/x-rar-compressed', 
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document', # docx
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',       # xlsx
        'text/csv', 'application/vnd.ms-excel'                                     # csv, xls
    ]
    
    valid_extensions = ['jpg', 'jpeg', 'png', 'pdf', 'zip', 'rar', 'docx', 'xlsx', 'csv', 'xls']
    
    file_mime_type = file.content_type
    file_extension = file.name.split('.')[-1].lower()

    if file_mime_type not in valid_mime_types or file_extension not in valid_extensions:
        raise ValidationError("Unsupported file type.")


class BlacklistedToken(models.Model):
    token = models.CharField(max_length=500)
    blacklisted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token


class User(models.Model):
    agent = models.CharField(max_length= 200 , null=True, blank=True )
    email = models.EmailField( null=True, blank=True)
    mobile = models.CharField(max_length=14)
    status = models.CharField(max_length=150 , null=True, blank=True)
    type = models.CharField(max_length=200)
    uniqueIdentifier = models.CharField(max_length=150 , unique=True)
    referal = models.CharField(max_length=14,  null=True, blank=True , unique=True) # معرف : کدملی معرف 
    attempts = models.IntegerField(default=0)
    lock_until = models.DateTimeField(null=True, blank=True)
    def lock(self):
        self.lock_until = timezone.now() + timedelta(minutes=5)     
        self.save()
    def is_locked(self):
        if self.lock_until and timezone.now() < self.lock_until:
            return True
        return False

    def __str__(self):
        uniqueIdentifier = self.uniqueIdentifier if self.uniqueIdentifier else "uniqueIdentifier"
        return f'{uniqueIdentifier}'
    

class accounts (models.Model) :
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    accountNumber = models.CharField(max_length=200)
    bank = models.CharField( max_length=200)
    branchCity = models.CharField( max_length=200)
    branchCode = models.CharField(max_length=20)
    branchName = models.CharField(max_length=200)
    isDefault = models.CharField( max_length=200)
    modifiedDate = models.CharField( max_length=200)
    type = models.CharField(max_length= 200)
    sheba = models.CharField(max_length= 200)


class LegalPerson (models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    citizenshipCountry = models.CharField( max_length=150 , null=True , blank= True)
    companyName = models.CharField( max_length=150 , null=True , blank= True)
    economicCode = models.CharField( max_length=150 , null=True , blank= True)
    evidenceExpirationDate = models.CharField( max_length=150 , null=True , blank= True)
    evidenceReleaseCompany = models.CharField( max_length=150 , null=True , blank= True)
    evidenceReleaseDate = models.CharField( max_length=150 , null=True , blank= True)
    legalPersonTypeSubCategory = models.CharField( max_length=150 , null=True , blank= True)
    registerDate = models.CharField( max_length=150 , null=True , blank= True)
    legalPersonTypeCategory = models.CharField( max_length=150 , null=True , blank= True)
    registerPlace = models.CharField( max_length=150 , null=True , blank= True)
    registerNumber = models.CharField( max_length=150 , null=True , blank= True)


class legalPersonShareholders (models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uniqueIdentifier = models.CharField( max_length=20 , null=True , blank= True)
    postalCode = models.CharField( max_length=20 , null=True , blank= True)
    positionType = models.CharField( max_length=50 , null=True , blank= True)
    percentageVotingRight = models.CharField( max_length=50 , null=True , blank= True)
    lastName = models.CharField( max_length=50 , null=True , blank= True)
    firstName = models.CharField( max_length=50 , null=True , blank= True)
    address = models.TextField( max_length=150 , null=True , blank= True)
    


class legalPersonStakeholders (models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uniqueIdentifier = models.CharField( max_length=150 , null=True , blank= True)
    type = models.CharField( max_length=150 , null=True , blank= True)
    startAt = models.CharField( max_length=150 , null=True , blank= True)
    positionType = models.CharField( max_length=150 , null=True , blank= True)
    lastName = models.CharField( max_length=150 , null=True , blank= True)
    isOwnerSignature = models.CharField( max_length=150 , null=True , blank= True)
    firstName = models.CharField( max_length=150 , null=True , blank= True)
    endAt = models.CharField( max_length=150 , null=True , blank= True)


class addresses (models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    alley = models.CharField(max_length=1000 ,  blank=True , null= True)
    city = models.CharField(max_length=1000 ,  blank=True , null= True)
    cityPrefix = models.CharField(max_length=1000 ,  blank=True , null= True)
    country =models.CharField(max_length=1000 ,  blank=True , null= True)
    countryPrefix = models.CharField(max_length=1000 ,  blank=True , null= True)
    email = models.EmailField ( blank=True , null= True)
    emergencyTel =  models.CharField(max_length=1000 ,  blank=True , null= True) 
    emergencyTelCityPrefix =  models.CharField(max_length=1000 ,  blank=True , null= True)
    emergencyTelCountryPrefix = models.CharField(max_length=1000 ,  blank=True , null= True)
    fax = models.CharField(max_length=1000 ,  blank=True , null= True)
    faxPrefix = models.CharField(max_length=1000 ,  blank=True , null= True)
    mobile = models.CharField(max_length=1000 ,  blank=True , null= True)
    plaque = models.CharField(max_length=1000 ,  blank=True , null= True)
    postalCode = models.CharField(max_length=1000 ,  blank=True , null= True)
    province = models.CharField(max_length=1000 ,  blank=True , null= True)
    remnantAddress = models.CharField(max_length=1000 ,  blank=True , null= True)
    section =models.CharField(max_length=1000 ,  blank=True , null= True)
    tel =  models.CharField(max_length=1000 ,  blank=True , null= True)
    website = models.CharField(max_length=1000 ,  blank=True , null= True)


class financialInfo (models.Model) :
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    assetsValue = models.CharField(max_length=1000 ,  blank=True , null= True , default="")
    cExchangeTransaction = models.CharField(max_length=1000 ,  blank=True , null= True)
    companyPurpose = models.CharField(max_length=1000 ,  blank=True , null= True)
    financialBrokers = models.CharField(max_length=1000 ,  blank=True , null= True)
    inComingAverage = models.CharField(max_length=1000 ,  blank=True , null= True)
    outExchangeTransaction = models.CharField(max_length=1000 ,  blank=True , null= True)
    rate = models.CharField(max_length=1000 ,  blank=True , null= True)
    rateDate = models.CharField(max_length=1000 ,  blank=True , null= True)
    referenceRateCompany = models.CharField(max_length=1000 ,  blank=True , null= True)
    sExchangeTransaction = models.CharField(max_length=1000 ,  blank=True , null= True)
    tradingKnowledgeLevel = models.CharField(max_length=1000 ,  blank=True , null= True)
    transactionLevel = models.CharField(max_length=1000 ,  blank=True , null= True)


class jobInfo (models.Model) :
    user = models.ForeignKey(User,on_delete=models.CASCADE)                   
    companyAddress = models.CharField(max_length=1000 ,  blank=True , null= True)
    companyCityPrefix = models.CharField(max_length=1000 ,  blank=True , null= True)
    companyEmail = models.CharField(max_length=1000 ,  blank=True , null= True)
    companyFax =  models.CharField(max_length=1000 ,  blank=True , null= True)
    companyFaxPrefix = models.CharField(max_length=1000 ,  blank=True , null= True)
    companyName = models.CharField(max_length=1000 ,  blank=True , null= True)
    companyPhone = models.CharField(max_length=1000 ,  blank=True , null= True)
    companyPostalCode = models.CharField(max_length=1000 ,  blank=True , null= True)
    companyWebSite = models.CharField(max_length=1000 ,  blank=True , null= True)
    employmentDate = models.CharField(max_length=1000 ,  blank=True , null= True)
    job = models.CharField(max_length=1000 ,  blank=True , null= True)
    jobDescription = models.CharField(max_length=1000 ,  blank=True , null= True)
    position = models.CharField(max_length=1000 ,  blank=True , null= True)


class privatePerson (models.Model) :
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    birthDate = models.CharField( max_length=200)
    fatherName = models.CharField(max_length=200)
    firstName = models.CharField(max_length=200)
    gender = models.CharField(max_length=200)
    lastName = models.CharField(max_length=200)
    placeOfBirth = models.CharField(max_length=200)
    placeOfIssue = models.CharField(max_length=200)
    seriSh = models.CharField(max_length=200)
    seriShChar = models.CharField(max_length=200, null=True, blank=True)
    serial = models.CharField(max_length=200)
    shNumber = models.CharField(max_length=200)
    signatureFile = models.FileField(upload_to='signatures/', null=True, blank=True,validators=[validate_file_type]) 


class tradingCodes (models.Model) :
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    code = models.CharField(max_length=200)
    firstPart =  models.CharField(max_length=200)
    secondPart  = models.CharField(max_length=200 , null=True, blank=True)
    thirdPart = models.CharField(max_length=200, null=True, blank=True)
    type = models.CharField(max_length=200, null=True, blank=True)


class Otp(models.Model):
    code = models.CharField(max_length=6)
    mobile = models.CharField(max_length=14)
    date = models.DateTimeField(auto_now_add=True)
    attempts  = models.IntegerField(default=0)
    locking = models.DateTimeField(blank= True , null= True) 
    expire = models.DateTimeField(blank=True, null=True)


class Admin(models.Model):
    firstName = models.CharField(max_length=32)
    lastName = models.CharField(max_length=32)
    mobile = models.CharField(max_length=11)
    uniqueIdentifier = models.CharField(max_length=10)
    email = models.EmailField()
    attempts = models.IntegerField(default=0)
    lock_until = models.DateTimeField(null=True, blank=True)
    def lock(self):
        self.lock_until = timezone.now() + timedelta(minutes=5)     
        self.save()
    def is_locked(self):
        if self.lock_until and timezone.now() < self.lock_until:
            return True
        return False
    def __str__(self):
        uniqueIdentifier = self.uniqueIdentifier if self.uniqueIdentifier else "uniqueIdentifier"
        return f'{uniqueIdentifier}'


class Reagent(models.Model):
    reference = models.ForeignKey(User,to_field='referal', on_delete=models.CASCADE , related_name='reagent_references') # معرفی کننده
    referrer = models.ForeignKey(User, on_delete=models.CASCADE , related_name='reagent_referrers') # معرفی شده
    date_created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'Reagent between {self.referrer} and {self.reference}'
    

class Captcha(models.Model):
    encrypted_response = models.TextField(max_length=6)
    enabled = models.BooleanField(default=True)

