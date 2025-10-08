import { useEffect, useMemo, useState } from 'react'
import {
  LayoutDashboard,
  Package2,
  TicketPercent,
  MessageCircle,
  Settings as SettingsIcon,
  PhoneCall,
  Mail,
} from 'lucide-react'
import './App.css'
import { PublicChatWidget } from './components/PublicChatWidget'

interface Product {
  id: number
  nameAr: string
  price: number
  sku?: string
  categories: string[]
  synced: boolean
}

interface VoucherImport {
  productId: number
  codes: string
  pushToZid: boolean
}

interface IntegrationStatus {
  name: string
  configured: boolean
  ok: boolean
  message: string
  checked_at: string
}

const SERVICE_LABELS: Record<string, string> = {
  zid: 'منصة زد',
  openai: 'OpenAI',
  whatsapp: 'واتساب',
  email: 'البريد المضمن',
}

const MENU_ITEMS = [
  { id: 'dashboard', label: 'لوحة التحكم', icon: LayoutDashboard },
  { id: 'products', label: 'المنتجات الرقمية', icon: Package2 },
  { id: 'vouchers', label: 'القسائم والأكواد', icon: TicketPercent },
  { id: 'communications', label: 'التواصل الفوري', icon: PhoneCall },
  { id: 'chat', label: 'محادثة الفريق', icon: MessageCircle },
  { id: 'settings', label: 'الإعدادات', icon: SettingsIcon },
]

const DEFAULT_DENOMS = ['2$', '5$', '10$', '25$', '50$', '100$']

function App() {
  const [activeMenu, setActiveMenu] = useState<string>('dashboard')
  const [theme, setTheme] = useState<string>(() => localStorage.getItem('theme') || 'corporate')
  const [products, setProducts] = useState<Product[]>([])
  const [productForm, setProductForm] = useState({
    nameAr: '',
    nameEn: '',
    price: 0,
    sku: '',
    autoCategories: true,
    pushToZid: true,
  })
  const [voucherForm, setVoucherForm] = useState<VoucherImport>({
    productId: 0,
    codes: '',
    pushToZid: true,
  })
  const [logs, setLogs] = useState<string[]>([
    'تم إنشاء الحساب الافتراضي للمسؤول',
    'تم تمكين الربط مع زد',
  ])
  const [whatsAppMessage, setWhatsAppMessage] = useState({
    to: '',
    template: 'digital_code',
    orderId: '',
    code: '',
    customer: '',
  })
  const [emailProvider, setEmailProvider] = useState<'gmail' | 'outlook'>('gmail')
  const [chatHistory, setChatHistory] = useState<string[]>([
    '👋 أهلاً بك في لوحة التحكم TwoCards',
  ])
  const [statusConfig, setStatusConfig] = useState({ baseUrl: 'http://localhost:8000', token: '' })
  const [statusResults, setStatusResults] = useState<IntegrationStatus[]>([])
  const [statusLoading, setStatusLoading] = useState(false)
  const [statusError, setStatusError] = useState<string | null>(null)

  useEffect(() => {
    document.documentElement.dataset.theme = theme
    document.documentElement.dir = 'rtl'
    document.documentElement.lang = 'ar'
    localStorage.setItem('theme', theme)
  }, [theme])

  const totals = useMemo(() => {
    const vouchersCount = voucherForm.codes
      .split('\n')
      .filter((line) => line.trim().length > 0).length
    return {
      products: products.length,
      vouchers: vouchersCount,
      synced: products.filter((p) => p.synced).length,
    }
  }, [products, voucherForm.codes])

  const handleCreateProduct = () => {
    if (!productForm.nameAr || productForm.price <= 0) {
      alert('يرجى تعبئة اسم المنتج والسعر بشكل صحيح')
      return
    }
    const categories = productForm.autoCategories ? DEFAULT_DENOMS : []
    const newProduct: Product = {
      id: Date.now(),
      nameAr: productForm.nameAr,
      price: productForm.price,
      sku: productForm.sku,
      categories,
      synced: productForm.pushToZid,
    }
    setProducts((prev) => [newProduct, ...prev])
    setLogs((prev) => [
      `✅ تم إنشاء المنتج ${productForm.nameAr}`,
      ...(productForm.pushToZid
        ? [`🚀 إرسال تلقائي إلى زد قيد المعالجة للمنتج ${productForm.nameAr}`]
        : []),
      ...prev,
    ])
    setProductForm({ nameAr: '', nameEn: '', price: 0, sku: '', autoCategories: true, pushToZid: true })
  }

  const handleImportVouchers = () => {
    if (!voucherForm.productId || !voucherForm.codes.trim()) {
      alert('يرجى اختيار المنتج وإدخال الأكواد')
      return
    }
    const count = voucherForm.codes
      .split('\n')
      .filter((line) => line.trim().length > 0).length
    setLogs((prev) => [
      `🎟️ تم استيراد ${count} كود للمنتج رقم ${voucherForm.productId}`,
      ...(voucherForm.pushToZid ? ['🔁 جاري المزامنة مع زد للأكواد المضافة'] : []),
      ...prev,
    ])
    setVoucherForm({ productId: voucherForm.productId, codes: '', pushToZid: voucherForm.pushToZid })
  }

  const handleSendWhatsApp = () => {
    if (!whatsAppMessage.to) {
      alert('أدخل رقم العميل')
      return
    }
    const preview = `مرحباً ${whatsAppMessage.customer}\nطلبك رقم ${whatsAppMessage.orderId}\nالكود: ${whatsAppMessage.code}`
    setLogs((prev) => [
      `📱 إرسال رسالة واتساب إلى ${whatsAppMessage.to}`,
      ...prev,
    ])
    alert(`سيتم إرسال الرسالة عبر واجهة واتساب:\n${preview}`)
  }

  const handleCheckStatus = async () => {
    const base = statusConfig.baseUrl.replace(/\/$/, '')
    setStatusLoading(true)
    setStatusError(null)
    try {
      const response = await fetch(`${base}/api/v1/system/status`, {
        headers: {
          'Content-Type': 'application/json',
          ...(statusConfig.token ? { Authorization: `Bearer ${statusConfig.token}` } : {}),
        },
      })
      if (!response.ok) {
        const text = await response.text()
        throw new Error(text || `فشل الطلب برمز ${response.status}`)
      }
      const data = await response.json()
      const services: IntegrationStatus[] = data.services || []
      setStatusResults(services)
      setLogs((prev) => [
        `🛰️ تم فحص حالة ${services.length} تكامل بشكل فوري`,
        ...prev,
      ])
    } catch (error) {
      setStatusResults([])
      setStatusError(error instanceof Error ? error.message : 'تعذر تنفيذ الفحص')
    } finally {
      setStatusLoading(false)
    }
  }

  const renderDashboard = () => (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-3">
        <div className="card bg-base-100 shadow">
          <div className="card-body">
            <span className="text-sm text-base-content/70">عدد المنتجات</span>
            <span className="text-3xl font-bold">{totals.products}</span>
          </div>
        </div>
        <div className="card bg-base-100 shadow">
          <div className="card-body">
            <span className="text-sm text-base-content/70">أكواد مضافة حديثاً</span>
            <span className="text-3xl font-bold">{totals.vouchers}</span>
          </div>
        </div>
        <div className="card bg-base-100 shadow">
          <div className="card-body">
            <span className="text-sm text-base-content/70">منتجات متزامنة مع زد</span>
            <span className="text-3xl font-bold">{totals.synced}</span>
          </div>
        </div>
      </div>
      <div className="card bg-base-100 shadow">
        <div className="card-body">
          <h2 className="card-title">آخر الأحداث</h2>
          <ul className="space-y-2 text-sm">
            {logs.slice(0, 6).map((log, index) => (
              <li key={index} className="flex items-center gap-2">
                <span className="badge badge-sm badge-primary" />
                <span>{log}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )

  const renderProducts = () => (
    <div className="grid gap-6 lg:grid-cols-[360px_1fr]">
      <div className="card bg-base-100 shadow">
        <div className="card-body space-y-4">
          <h2 className="card-title">إضافة منتج رقمي</h2>
          <label className="form-control">
            <span className="label-text">اسم المنتج (عربي)</span>
            <input
              type="text"
              className="input input-bordered"
              value={productForm.nameAr}
              onChange={(e) => setProductForm((prev) => ({ ...prev, nameAr: e.target.value }))}
            />
          </label>
          <label className="form-control">
            <span className="label-text">اسم المنتج (إنجليزي)</span>
            <input
              type="text"
              className="input input-bordered"
              value={productForm.nameEn}
              onChange={(e) => setProductForm((prev) => ({ ...prev, nameEn: e.target.value }))}
            />
          </label>
          <label className="form-control">
            <span className="label-text">السعر (ريال)</span>
            <input
              type="number"
              className="input input-bordered"
              value={productForm.price}
              onChange={(e) => setProductForm((prev) => ({ ...prev, price: Number(e.target.value) }))}
            />
          </label>
          <label className="form-control">
            <span className="label-text">رمز SKU</span>
            <input
              type="text"
              className="input input-bordered"
              value={productForm.sku}
              onChange={(e) => setProductForm((prev) => ({ ...prev, sku: e.target.value }))}
            />
          </label>
          <label className="label cursor-pointer justify-start gap-4">
            <input
              type="checkbox"
              className="checkbox checkbox-primary"
              checked={productForm.autoCategories}
              onChange={(e) => setProductForm((prev) => ({ ...prev, autoCategories: e.target.checked }))}
            />
            <span className="label-text">إضافة الفئات الافتراضية ({DEFAULT_DENOMS.join('، ')})</span>
          </label>
          <label className="label cursor-pointer justify-start gap-4">
            <input
              type="checkbox"
              className="checkbox checkbox-primary"
              checked={productForm.pushToZid}
              onChange={(e) => setProductForm((prev) => ({ ...prev, pushToZid: e.target.checked }))}
            />
            <span className="label-text">مزامنة مباشرة مع زد</span>
          </label>
          <button className="btn btn-primary w-full" onClick={handleCreateProduct}>
            حفظ المنتج وإرساله
          </button>
        </div>
      </div>
      <div className="card bg-base-100 shadow">
        <div className="card-body">
          <h2 className="card-title">قائمة المنتجات</h2>
          <div className="overflow-x-auto">
            <table className="table">
              <thead>
                <tr>
                  <th>المنتج</th>
                  <th>السعر</th>
                  <th>SKU</th>
                  <th>الحالة</th>
                </tr>
              </thead>
              <tbody>
                {products.length === 0 && (
                  <tr>
                    <td colSpan={4} className="text-center text-base-content/60">
                      لم يتم إضافة منتجات بعد
                    </td>
                  </tr>
                )}
                {products.map((product) => (
                  <tr key={product.id}>
                    <td>
                      <div className="font-semibold">{product.nameAr}</div>
                      <div className="text-xs text-base-content/60">
                        {product.categories.length ? `فئات: ${product.categories.join('، ')}` : 'بدون فئات مخصصة'}
                      </div>
                    </td>
                    <td>{product.price.toFixed(2)} ر.س</td>
                    <td>{product.sku || '-'}</td>
                    <td>
                      <span className={`badge ${product.synced ? 'badge-success' : 'badge-ghost'}`}>
                        {product.synced ? 'متزامن مع زد' : 'محلي فقط'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )

  const renderVouchers = () => (
    <div className="grid gap-6 lg:grid-cols-[360px_1fr]">
      <div className="card bg-base-100 shadow">
        <div className="card-body space-y-4">
          <h2 className="card-title">استيراد أكواد</h2>
          <label className="form-control">
            <span className="label-text">المنتج المرتبط</span>
            <select
              className="select select-bordered"
              value={voucherForm.productId}
              onChange={(e) => setVoucherForm((prev) => ({ ...prev, productId: Number(e.target.value) }))}
            >
              <option value={0}>اختر المنتج</option>
              {products.map((product) => (
                <option key={product.id} value={product.id}>
                  {product.nameAr}
                </option>
              ))}
            </select>
          </label>
          <label className="form-control">
            <span className="label-text">أكواد متعددة (كل سطر يمثل كود)</span>
            <textarea
              className="textarea textarea-bordered h-40"
              value={voucherForm.codes}
              onChange={(e) => setVoucherForm((prev) => ({ ...prev, codes: e.target.value }))}
            />
          </label>
          <label className="label cursor-pointer justify-start gap-4">
            <input
              type="checkbox"
              className="checkbox checkbox-primary"
              checked={voucherForm.pushToZid}
              onChange={(e) => setVoucherForm((prev) => ({ ...prev, pushToZid: e.target.checked }))}
            />
            <span className="label-text">إرسال الأكواد مباشرة إلى زد</span>
          </label>
          <button className="btn btn-primary w-full" onClick={handleImportVouchers}>
            استيراد الأكواد الآن
          </button>
        </div>
      </div>
      <div className="card bg-base-100 shadow">
        <div className="card-body space-y-4">
          <h2 className="card-title">سجل العمليات</h2>
          <ul className="space-y-2 text-sm">
            {logs.slice(0, 10).map((log, index) => (
              <li key={index} className="flex items-center gap-2">
                <span className="badge badge-xs badge-secondary" />
                <span>{log}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )

  const renderCommunications = () => (
    <div className="grid gap-6 lg:grid-cols-2">
      <div className="card bg-base-100 shadow">
        <div className="card-body space-y-4">
          <h2 className="card-title flex items-center gap-2">
            <PhoneCall className="size-5" />
            إرسال رسالة واتساب
          </h2>
          <div className="grid gap-3">
            <label className="form-control">
              <span className="label-text">رقم العميل</span>
              <input
                type="text"
                className="input input-bordered"
                value={whatsAppMessage.to}
                onChange={(e) => setWhatsAppMessage((prev) => ({ ...prev, to: e.target.value }))}
              />
            </label>
            <label className="form-control">
              <span className="label-text">اسم العميل</span>
              <input
                type="text"
                className="input input-bordered"
                value={whatsAppMessage.customer}
                onChange={(e) => setWhatsAppMessage((prev) => ({ ...prev, customer: e.target.value }))}
              />
            </label>
            <label className="form-control">
              <span className="label-text">رقم الطلب</span>
              <input
                type="text"
                className="input input-bordered"
                value={whatsAppMessage.orderId}
                onChange={(e) => setWhatsAppMessage((prev) => ({ ...prev, orderId: e.target.value }))}
              />
            </label>
            <label className="form-control">
              <span className="label-text">الكود / الرمز</span>
              <input
                type="text"
                className="input input-bordered"
                value={whatsAppMessage.code}
                onChange={(e) => setWhatsAppMessage((prev) => ({ ...prev, code: e.target.value }))}
              />
            </label>
          </div>
          <button className="btn btn-success w-full" onClick={handleSendWhatsApp}>
            إرسال الرسالة عبر واتساب
          </button>
        </div>
      </div>
      <div className="card bg-base-100 shadow">
        <div className="card-body space-y-4">
          <h2 className="card-title flex items-center gap-2">
            <Mail className="size-5" />
            البريد المدمج
          </h2>
          <div className="flex gap-3">
            <button
              className={`btn btn-sm ${emailProvider === 'gmail' ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setEmailProvider('gmail')}
            >
              Gmail
            </button>
            <button
              className={`btn btn-sm ${emailProvider === 'outlook' ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setEmailProvider('outlook')}
            >
              Outlook
            </button>
          </div>
          <div className="rounded-lg border border-base-300">
            <iframe
              title="mail"
              src={emailProvider === 'gmail' ? 'https://mail.google.com' : 'https://outlook.office.com/mail'}
              className="h-80 w-full rounded-lg"
            />
          </div>
        </div>
      </div>
      <div className="card bg-base-100 shadow">
        <div className="card-body space-y-4">
          <h2 className="card-title flex items-center gap-2">
            <span className="avatar placeholder size-8">
              <span className="rounded-full bg-primary/10 text-primary">⚙️</span>
            </span>
            فحص الربط الفوري
          </h2>
          <p className="text-sm text-base-content/70">
            استخدم هذه الأداة للتحقق من تفعيل الربط مع زد، OpenAI، واتساب والبريد داخل خادمك الفعلي.
          </p>
          <label className="form-control">
            <span className="label-text">رابط الخادم الخلفي</span>
            <input
              type="text"
              className="input input-bordered"
              value={statusConfig.baseUrl}
              onChange={(event) => setStatusConfig((prev) => ({ ...prev, baseUrl: event.target.value }))}
              placeholder="http://localhost:8000"
            />
          </label>
          <label className="form-control">
            <span className="label-text">رمز الدخول (JWT)</span>
            <input
              type="password"
              className="input input-bordered"
              value={statusConfig.token}
              onChange={(event) => setStatusConfig((prev) => ({ ...prev, token: event.target.value }))}
              placeholder="eyJhbGciOi..."
            />
          </label>
          <button className="btn btn-primary" onClick={handleCheckStatus} disabled={statusLoading}>
            {statusLoading ? 'جارٍ التحقق...' : 'تشغيل الاختبار'}
          </button>
          {statusError && (
            <div className="alert alert-error text-sm">
              <span>تعذر الوصول: {statusError}</span>
            </div>
          )}
          <div className="space-y-3">
            {statusResults.length === 0 ? (
              <p className="text-sm text-base-content/60">
                ستظهر نتيجة كل تكامل بعد الضغط على زر الاختبار باستخدام بيانات الدخول الصحيحة.
              </p>
            ) : (
              statusResults.map((status) => (
                <div key={status.name} className="rounded-xl border border-base-300 p-3">
                  <div className="flex items-center justify-between">
                    <span className="font-medium">{SERVICE_LABELS[status.name] ?? status.name}</span>
                    <span
                      className={`badge ${
                        status.ok ? 'badge-success' : status.configured ? 'badge-warning' : 'badge-ghost'
                      }`}
                    >
                      {status.ok ? 'متصل' : status.configured ? 'يتطلب مراجعة' : 'غير مُعد'}
                    </span>
                  </div>
                  <p className="mt-2 text-xs text-base-content/70">{status.message}</p>
                  <p className="mt-1 text-[10px] text-base-content/50">آخر فحص: {status.checked_at}</p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )

  const renderChat = () => (
    <div className="card bg-base-100 shadow">
      <div className="card-body space-y-4">
        <h2 className="card-title">المحادثة الداخلية</h2>
        <div className="h-80 overflow-y-auto rounded-lg border border-dashed border-base-300 bg-base-200 p-4">
          <ul className="space-y-3 text-sm">
            {chatHistory.map((message, index) => (
              <li key={index} className="rounded-lg bg-base-100 p-3 shadow-sm">
                {message}
              </li>
            ))}
          </ul>
        </div>
        <div className="flex gap-2">
          <input
            type="text"
            className="input input-bordered flex-1"
            placeholder="أكتب رسالة أو أمر مثل /logs 10"
            onKeyDown={(event) => {
              if (event.key === 'Enter') {
                const value = (event.target as HTMLInputElement).value
                if (!value.trim()) return
                setChatHistory((prev) => [...prev, `🙍‍♂️ ${value}`])
                if (value.startsWith('/logs')) {
                  setChatHistory((prev) => [...prev, '🤖 أحدث 3 سجلات: ', ...logs.slice(0, 3)])
                }
                ;(event.target as HTMLInputElement).value = ''
              }
            }}
          />
          <button
            className="btn"
            onClick={() => setChatHistory((prev) => [...prev, '🤖 تم تبديل السمة إلى الوضع الداكن'])}
          >
            /theme dark
          </button>
        </div>
      </div>
    </div>
  )

  const renderSettings = () => (
    <div className="grid gap-6 lg:grid-cols-2">
      <div className="card bg-base-100 shadow">
        <div className="card-body space-y-4">
          <h2 className="card-title">مفاتيح الربط والتكامل</h2>
          <label className="form-control">
            <span className="label-text">رمز زد (ZID_TOKEN)</span>
            <input type="password" className="input input-bordered" placeholder="••••••••" />
          </label>
          <label className="form-control">
            <span className="label-text">مفتاح OpenAI</span>
            <input type="password" className="input input-bordered" placeholder="sk-xxxxxxxx" />
          </label>
          <label className="form-control">
            <span className="label-text">رمز واتساب</span>
            <input type="password" className="input input-bordered" placeholder="EAAG..." />
          </label>
          <label className="form-control">
            <span className="label-text">معرّف رقم واتساب</span>
            <input type="text" className="input input-bordered" placeholder="123456789" />
          </label>
          <button className="btn btn-primary">حفظ التغييرات</button>
        </div>
      </div>
      <div className="card bg-base-100 shadow">
        <div className="card-body space-y-4">
          <h2 className="card-title">خيارات الواجهة</h2>
          <div className="flex flex-wrap gap-2">
            <button
              className={`btn btn-sm ${theme === 'corporate' ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setTheme('corporate')}
            >
              الوضع الرسمي
            </button>
            <button
              className={`btn btn-sm ${theme === 'dark' ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setTheme('dark')}
            >
              الوضع الداكن
            </button>
            <button
              className={`btn btn-sm ${theme === 'light' ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setTheme('light')}
            >
              الوضع الفاتح
            </button>
          </div>
          <div className="alert alert-info">
            <span>
              يتم حفظ التفضيل لكل مستخدم وسيتم المزامنة بعد تسجيل الدخول.
            </span>
          </div>
        </div>
      </div>
    </div>
  )

  const renderContent = () => {
    switch (activeMenu) {
      case 'products':
        return renderProducts()
      case 'vouchers':
        return renderVouchers()
      case 'communications':
        return renderCommunications()
      case 'chat':
        return renderChat()
      case 'settings':
        return renderSettings()
      default:
        return renderDashboard()
    }
  }

  return (
    <div className="min-h-screen bg-base-200">
      <div className="grid min-h-screen gap-6 px-4 py-6 lg:grid-cols-[240px_1fr] lg:px-10">
        <aside className="rounded-3xl bg-base-100 shadow-xl">
          <div className="p-6">
            <div className="flex flex-col items-center gap-3">
              <div className="avatar placeholder">
                <div className="w-16 rounded-full bg-primary text-primary-content">
                  <span className="text-xl font-bold">2C</span>
                </div>
              </div>
              <div className="text-center">
                <h1 className="text-lg font-bold">منصة توكاردز</h1>
                <p className="text-xs text-base-content/60">إدارة متكاملة للمنتجات الرقمية</p>
              </div>
            </div>
            <nav className="mt-8 space-y-2">
              {MENU_ITEMS.map((item) => (
                <button
                  key={item.id}
                  onClick={() => setActiveMenu(item.id)}
                  className={`flex w-full items-center gap-3 rounded-xl px-4 py-3 text-right transition ${
                    activeMenu === item.id ? 'bg-primary text-primary-content shadow-lg' : 'hover:bg-base-200'
                  }`}
                >
                  <item.icon className="size-5" />
                  <span className="text-sm font-medium">{item.label}</span>
                </button>
              ))}
            </nav>
          </div>
        </aside>
        <main className="space-y-6">
          <header className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <h2 className="text-2xl font-bold text-base-content">{MENU_ITEMS.find((item) => item.id === activeMenu)?.label}</h2>
              <p className="text-sm text-base-content/60">
                منصة موحدة لإدارة البطاقات الرقمية، المزامنة مع زد، الذكاء الاصطناعي، والدعم الفوري.
              </p>
            </div>
            <div className="flex items-center gap-3">
              <span className="badge badge-lg badge-outline">المسؤول: admin</span>
              <button className="btn btn-outline btn-sm" onClick={() => setTheme(theme === 'dark' ? 'corporate' : 'dark')}>
                تبديل السمة
              </button>
            </div>
          </header>
          {renderContent()}
        </main>
      </div>
      <PublicChatWidget />
    </div>
  )
}

export default App
