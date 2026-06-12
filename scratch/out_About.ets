```typescript
@Entry
@Component
struct About {
  build() {
    Stack() {
      Column() {
        Text("OSChina.NET for Android")
          .fontSize(16)
          .fontWeight(FontWeight.Bold)
          .fontColor(Color.Black)
          .margin({ bottom: 200 })
        
        Text("版本：1.0.0")
          .fontColor(Color.Black)
          .margin({ bottom: 160 })
        
        Button("检查新版本")
          .width(100)
          .margin({ bottom: 110 })
          .onClick(() => {
            //