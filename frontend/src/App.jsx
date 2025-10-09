import React, { useEffect, useState } from "react";
import { api } from "./api";

export default function App() {
  const [products, setProducts] = useState([]);
  const [status, setStatus] = useState("loading...");
  const [order, setOrder] = useState([]);

  useEffect(() => {
    api
      .get("/healthz")
      .then(() => setStatus("✅ backend ok"))
      .catch(() => setStatus("❌ backend down"));
    api
      .get("/products")
      .then((r) => setProducts(r.data || []))
      .catch(() => setProducts([]));
  }, []);

  const addToCart = (product) => {
    setOrder((prev) => {
      const existing = prev.find((item) => item.product_id === product.id);
      if (existing) {
        return prev.map((item) =>
          item.product_id === product.id
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      }
      return [
        ...prev,
        {
          product_id: product.id,
          quantity: 1,
          unit_price: product.price,
          name: product.name,
        },
      ];
    });
  };

  const submitOrder = async () => {
    if (!order.length) {
      return alert("السلة فارغة");
    }
    const payload = {
      customer_name: "Demo",
      items: order.map(({ product_id, quantity, unit_price }) => ({
        product_id,
        quantity,
        unit_price,
      })),
    };
    const res = await api.post("/orders", payload);
    alert("تم إنشاء الطلب #" + res.data.id);
    setOrder([]);
  };

  return (
    <div
      style={{
        fontFamily: "system-ui,Arial",
        padding: 24,
        maxWidth: 980,
        margin: "0 auto",
      }}
    >
      <h1>TwoCards Store</h1>
      <div style={{ marginBottom: 8, color: "#64748b" }}>
        {status} — API: {api.defaults.baseURL}
      </div>

      <h2>المنتجات</h2>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill,minmax(220px,1fr))",
          gap: 12,
        }}
      >
        {products.map((product) => (
          <div
            key={product.id}
            style={{
              border: "1px solid #e2e8f0",
              borderRadius: 12,
              padding: 12,
            }}
          >
            <div style={{ fontWeight: 600 }}>{product.name}</div>
            <div style={{ fontSize: 13, color: "#64748b" }}>
              {product.description || "-"}
            </div>
            <div style={{ margin: "8px 0" }}>
              {product.price.toFixed(2)} ر.س
            </div>
            <button onClick={() => addToCart(product)}>أضف للسلة</button>
          </div>
        ))}
        {!products.length && <div>لا توجد منتجات بعد.</div>}
      </div>

      <h2 style={{ marginTop: 24 }}>السلة</h2>
      {order.length ? (
        <div>
          {order.map((item, index) => (
            <div
              key={index}
              style={{
                display: "flex",
                justifyContent: "space-between",
                borderBottom: "1px solid #e2e8f0",
                padding: "6px 0",
              }}
            >
              <div>{item.name}</div>
              <div>x{item.quantity}</div>
              <div>{(item.unit_price * item.quantity).toFixed(2)} ر.س</div>
            </div>
          ))}
          <div style={{ marginTop: 10 }}>
            <button onClick={submitOrder}>إرسال الطلب</button>
          </div>
        </div>
      ) : (
        <div>السلة فارغة.</div>
      )}
    </div>
  );
}
