# Script thuyết trình slide 17-22

File này dùng cho phần thuyết trình từ slide 17 đến slide 22 của deck `main.pdf`.
Mỗi slide gồm hai phần:

- **Script nói**: phần có thể đọc trực tiếp khi trình bày.
- **Giải thích hình/biểu đồ**: phần dùng để nói kỹ hơn hoặc trả lời câu hỏi.

Lưu ý: trong PDF hiện tại, slide 22 là slide giới thiệu sweep tham số `a`; biểu đồ sweep `a` nằm ở slide 23. Phần slide 22 bên dưới có thêm câu nối để dẫn sang biểu đồ đó.

## Slide 17 - Time Stepping: Corrective Algorithm - Visual Summary

### Script nói

Ở slide này, em tóm tắt cách mô phỏng xử lý va chạm sau mỗi bước Euler.

Trong mô hình một chiều, tất cả người đi bộ có chiều chuyển động dự định theo trục `+x`. Vì vậy người ở phía trước pedestrian `i` được quy ước là pedestrian `i+1`, và khoảng cách phía trước được tính theo điều kiện tuần hoàn của hành lang.

Thuật toán gồm bốn bước. Bước một là **predict**: từ vận tốc hiện tại và lực tác động, ta tính vận tốc mới và vị trí mới bằng một bước Euler. Bước hai là **check**: ta so sánh khoảng cách thật sự `s_i` từ pedestrian `i` đến pedestrian `i+1` với độ dài yêu cầu `d_i = a + b v_i`. Nếu `s_i` nhỏ hơn `d_i`, nghĩa là bước Euler vừa dự đoán một trạng thái bị chồng lấn hoặc quá gần nhau.

Bước ba là **correct**: pedestrian `i` bị dừng lại, vận tốc đặt về 0 và vị trí được khôi phục về vị trí cũ trước bước Euler. Bước bốn là **propagate**: khi pedestrian `i` bị dừng lại, người phía sau `i-1` có thể bây giờ lại quá gần pedestrian `i`, nên ta phải kiểm tra tiếp. Quá trình này lặp lại cho đến khi không còn overlap nào trong hệ thống.

Điểm quan trọng của slide này là correction không phải chỉ sửa một người độc lập. Trong dòng một hàng, một người dừng lại có thể tạo thành một chuỗi tác động ngược về phía sau. Với điều kiện biên tuần hoàn, chuỗi này còn có thể vòng qua đầu hành lang.

### Giải thích hình

- Hàng đầu tiên minh họa bước **Predict**. Chấm xanh là pedestrian `i`, chấm đỏ là pedestrian `i+1`, tức người ở phía trước. Mũi tên đứt nét cho thấy vị trí dự đoán mới của pedestrian `i` sau một bước Euler.
- Hàng thứ hai là bước **Check**. Đoạn `s_i` là khoảng cách thực tế giữa hai người sau khi dự đoán. Đoạn `d_i` là khoảng cách tối thiểu mà mô hình yêu cầu. Khi `s_i <= d_i`, trạng thái này vi phạm điều kiện hard-body.
- Hàng thứ ba là bước **Correct**. Pedestrian `i` không được giữ vị trí dự đoán nữa mà quay về vị trí cũ, đồng thời vận tốc được đặt về 0. Cách này giữ được ràng buộc không vượt qua và không chồng lấn.
- Hàng cuối là **Propagate / Cascade**. Khi pedestrian `i` dừng lại, pedestrian `i-1` ở phía sau có thể không còn đủ khoảng trống, nên cần re-check `i-1`. Đây là cơ chế tạo ra hiệu ứng hàng đợi trong mô phỏng.
- Nếu được hỏi về biên tuần hoàn: khoảng cách được hiểu modulo `L`, nên người gần cuối hành lang vẫn có thể có người phía trước là người ở đầu hành lang.

### Câu chốt

Slide này đảm bảo logic vi mô của mô hình: mỗi bước thời gian đều cho phép di chuyển trước, sau đó sửa các vi phạm hard-body theo đúng thứ tự một hàng.

## Slide 18 - Simulation Setup

### Script nói

Slide này tóm tắt cấu hình dùng cho các thí nghiệm.

Môi trường mô phỏng là hành lang một chiều có điều kiện biên tuần hoàn, với chiều dài `L = 17.3 m`. Nghĩa là khi pedestrian đi hết cuối hành lang, họ quay lại đầu hành lang, nên mật độ pedestrian được giữ ổn định trong quá trình mô phỏng.

Vận tốc mong muốn của pedestrian được lấy từ phân phối gần normal, với trung bình `mu = 1.24 m/s` và độ lệch chuẩn `sigma = 0.05 m/s`. Tham số `tau = 0.61 s` là thời gian thư giãn, biểu diễn mức độ nhanh chậm mà pedestrian điều chỉnh vận tốc hiện tại về vận tốc mong muốn. Tham số `a = 0.36 m` là khoảng cách tối thiểu khi pedestrian đứng yên.

Về protocol, mỗi cấu hình được chạy `3 x 10^5` bước relaxation trước để hệ thống bỏ qua transient ban đầu. Sau đó ta tiếp tục chạy `3 x 10^5` bước measurement để tính vận tốc trung bình và vẽ fundamental diagram.

Các chấm empirical trong các biểu đồ sau được lấy bằng plot digitization từ dữ liệu tham chiếu Seyfried et al. (2005), dùng để so sánh hình dạng velocity-density curve của mô hình với dữ liệu thực nghiệm.

### Giải thích nội dung

- `L = 17.3 m` là độ dài hành lang tuần hoàn; mật độ được tính theo `rho = N / L`.
- `v0_mean = 1.24 m/s` là tốc độ mong muốn trung bình khi không bị cản trở.
- `v0_std = 0.05 m/s` tạo ra khác biệt nhỏ giữa các pedestrian, giúp mô phỏng không quá đồng nhất.
- `tau = 0.61 s` điều khiển độ mạnh của xu hướng trở về vận tốc mong muốn.
- `a = 0.36 m` là phần độ dài cơ bản trong `d_i(t) = a + b v_i(t)`.
- Relaxation và measurement cùng dài để kết quả không phụ thuộc quá nhiều vào trạng thái khởi tạo.

### Câu chốt

Tất cả biểu đồ phía sau đều dùng cùng một nền mô phỏng này; ta chỉ thay đổi một vài tham số như `b`, remote action, hoặc `a` để phân tích tác động của từng thành phần trong mô hình.

## Slide 19 - Hard-body Model without Remote Action

### Script nói

Slide này trả lời câu hỏi: nếu chỉ dùng hard-body constraint, không có remote action, thì tham số `b` trong `d_i = a + b v_i` ảnh hưởng thế nào đến fundamental diagram.

Trục ngang là mật độ `rho`, đơn vị `1/m`. Trục dọc là vận tốc trung bình `v bar`, đơn vị `m/s`. Các chấm xám là dữ liệu empirical Seyfried 2005. Ba đường màu là kết quả mô phỏng với ba giá trị `b`: `b = 0`, `b = 0.56`, và `b = 1.06`.

Khi `b = 0`, required space chỉ là hằng số `a`. Điều này có nghĩa là pedestrian đang đi nhanh hay chậm đều bị áp cùng một khoảng cách tối thiểu. Kết quả là đường màu xanh không giảm đúng theo empirical: vận tốc bị duy trì quá cao ở vùng mật độ trung bình và cao, nên hình dạng fundamental diagram sai.

Khi `b = 0.56 s`, required space tăng theo vận tốc. Pedestrian đi nhanh cần nhiều khoảng trống hơn, pedestrian chậm lại cần ít khoảng trống hơn. Đường màu cam vì vậy bám sát hơn với xu hướng empirical: vận tốc giảm mềm hơn theo mật độ và tạo được dạng cong đúng hơn.

Khi `b = 1.06 s`, tác động velocity-dependent spacing quá mạnh. Pedestrian cần khoảng cách quá lớn khi đang đi nhanh, nên mô hình dự đoán tắc nghẽn sớm hơn và vận tốc giảm quá nhanh so với empirical.

Kết luận của slide này là: hard-body model chỉ có thể tái hiện dữ liệu thực nghiệm nếu required space phụ thuộc vào vận tốc, tức `b > 0`. Trong các giá trị thử nghiệm, `b = 0.56 s` là giá trị hợp lý nhất với dữ liệu Seyfried.

### Giải thích biểu đồ

- **Trục x**: density `rho = N/L`. Khi `rho` tăng, số pedestrian trên cùng một chiều dài hành lang tăng.
- **Trục y**: mean velocity, tính sau giai đoạn relaxation.
- **Chấm xám**: dữ liệu empirical digitized. Đây là mốc để xem mô hình có đúng shape hay không, không phải kết quả simulation.
- **Đường xanh `b = 0`**: required length không phụ thuộc tốc độ. Đường này overestimate vận tốc ở mật độ cao, nên không bắt được congestion onset đúng.
- **Đường cam `b = 0.56`**: tạo sự giảm vận tốc mềm và gần empirical nhất trong ba curve.
- **Đường tím `b = 1.06`**: spacing tăng quá nhanh theo vận tốc, làm dòng người bị cản trở sớm hơn.
- **Thông điệp vật lý**: `b` không chỉ là tham số fit. Nó đại diện cho việc người đi bộ cần nhiều khoảng trống hơn khi đi nhanh.

### Câu chốt

Không có remote action, thành phần quan trọng nhất để match empirical trend là velocity-dependent space: `d_i = a + b v_i`.

## Slide 20 - Hard-body Model with Remote Action

### Script nói

Slide này thêm remote action vào mô hình để xem lực từ xa có làm thay đổi fundamental diagram hay không.

Ba đường trên biểu đồ có cùng trục như slide trước: trục ngang là density, trục dọc là mean velocity. Đường xanh là baseline không remote action với `b = 0.56`. Đường cam là có remote action nhưng `b = 0`. Đường tím là có remote action và `b = 0.56`.

Kết quả đầu tiên là với `b = 0.56`, thêm remote action không làm thay đổi lớn về dạng tổng thể của curve. Nó có thể làm một số điểm ở mật độ cao thấp hơn, nhưng shape chính vẫn là một đường giảm liên tục từ free flow sang congested flow. Điều này cho thấy khi required space đã được calibrate theo vận tốc, hard-body constraint đã nắm được phần lớn hành vi macroscopic.

Kết quả thứ hai quan trọng hơn: với `b = 0`, remote action tạo ra một "velocity gap" không vật lý quanh `rho` xấp xỉ `1.2 1/m`. Đường cam giữ vận tốc cao trong một khoảng mật độ, sau đó rơi rất mạnh. Nghĩa là quá trình chuyển từ free flow sang congested flow không còn mềm nữa.

Giải thích là remote action chỉ thêm một lực đẩy/hãm từ xa, nhưng nó không thay thế được việc required space phải thay đổi theo vận tốc. Nếu `b = 0`, pedestrian vẫn bị ép dùng một khoảng cách cố định, nên khi mật độ vượt ngưỡng, hệ thống dễ chuyển đột ngột sang trạng thái jam.

### Giải thích biểu đồ

- **Đường xanh**: no remote action, `b = 0.56`. Đây là baseline đã fit tốt hơn ở slide 19.
- **Đường tím**: remote action, `b = 0.56`. Curve gần với baseline về xu hướng chính, cho thấy remote action không phải yếu tố quyết định nếu `b` đã hợp lý.
- **Đường cam**: remote action, `b = 0`. Vận tốc ở vùng mật độ thấp-trung bình vẫn cao, nhưng sau đó bị sụp nhanh. Đây là "velocity gap".
- **Velocity gap**: thay vì giảm đều theo density, hệ thống có một chuyển pha đột ngột giữa trạng thái đi nhanh và trạng thái tắc nghẽn.
- **Thông điệp model**: remote action có thể tạo anticipatory braking, nhưng nếu spacing law sai, kết quả macroscopic vẫn sai.

### Câu chốt

Remote action không sửa được lỗi của `b = 0`. Yếu tố cần thiết để có fundamental diagram hợp lý vẫn là khoảng cách yêu cầu phụ thuộc vận tốc.

## Slide 21 - Microscopic Mechanism: Stop-and-Go Waves

### Script nói

Slide này nhìn vào cơ chế vi mô phía sau velocity gap. Thay vì chỉ xem vận tốc trung bình, ở đây ta vẽ vị trí của từng pedestrian theo thời gian.

Biểu đồ gồm hai panel. Panel bên trái là `rho = 1.16 1/m`, panel bên phải là `rho = 1.21 1/m`. Hai mật độ này rất gần nhau, nhưng nằm ở quanh ngưỡng mà mô hình `b = 0` bắt đầu mất ổn định. Trục ngang là vị trí `x` trên hành lang tuần hoàn dài `17.3 m`. Trục dọc là frame index; thời gian tăng từ trên xuống dưới. Các vòng tròn xám là vị trí của tất cả pedestrian ở từng frame, còn các chấm đen theo dõi riêng một pedestrian.

Ở mật độ thấp hơn, trajectory của pedestrian được highlight thay đổi tương đối đều hơn. Hệ thống vẫn có tương tác và dao động nhỏ, nhưng chưa tạo ra sóng dừng-lại rõ ràng. Khi tăng mật độ lên chỉ một lượng nhỏ, sang `rho = 1.21`, ta bắt đầu thấy các cụm điểm dày hơn và trajectory có những đoạn bị chậm/dừng rõ hơn. Đây là dấu hiệu của stop-and-go wave: một pedestrian phía trước chậm lại, người phía sau phải phanh, và tác động này lan ngược về phía sau hàng.

Điểm cần nói ở đây là velocity gap trên slide 20 không chỉ là artifact trên biểu đồ trung bình. Nó có cơ chế vi mô: sau ngưỡng mật độ, những dao động nhỏ trong khoảng cách bị khuếch đại thành sóng dừng-lại. Nếu `b > 0`, khi pedestrian chậm lại thì required space `d(v)` cũng giảm theo, tạo thêm damping tự nhiên và làm sóng này khó bị khuếch đại hơn.

### Giải thích biểu đồ

- **Trục x**: position `x` trong hành lang tuần hoàn. Khi pedestrian vượt qua cuối hành lang, vị trí quay lại gần 0.
- **Trục y**: frame index. Do trục y bị đảo ngược, đọc từ trên xuống dưới là thời gian tăng.
- **Vòng tròn xám**: tất cả pedestrian tại mỗi frame. Mỗi hàng ngang gần với một snapshot của hệ thống.
- **Chấm đen**: một pedestrian được track qua các frame, giúp thấy đổi chuyển động của một cá thể thay vì chỉ nhìn toàn bộ đám đông.
- **Chuỗi điểm nghiêng đều**: pedestrian đi tương đối ổn định.
- **Cụm điểm dày hoặc gần thẳng đứng**: pedestrian chậm lại hoặc dừng trong nhiều frame, tạo dấu hiệu tắc nghẽn cục bộ.
- **So sánh hai panel**: chỉ tăng mật độ từ `1.16` lên `1.21 1/m` nhưng hệ thống chuyển từ gần ổn định sang có dao động được khuếch đại.
- **Kết nối với slide 20**: đây là lý do đường velocity-density có thể rơi đột ngột khi `b = 0`.

### Câu chốt

Stop-and-go wave là cơ chế vi mô giải thích vì sao một thay đổi nhỏ về density có thể tạo ra thay đổi lớn trong mean velocity.

## Slide 22 - Parameter Analysis: New Sweep

### Script nói

Sau khi đã phân tích `b` và remote action, slide này giới thiệu một sweep tham số mới để phần analysis khác với việc chỉ lặp lại velocity dispersion hoặc thay đổi chiều dài hành lang.

Tham số được thay đổi là `a` trong công thức:

```text
d_i(t) = a + b v_i(t)
```

Nếu `b` là phần khoảng cách tăng thêm theo vận tốc, thì `a` là phần baseline: khoảng cách tối thiểu luôn tồn tại kể cả khi pedestrian đi rất chậm hoặc gần như đứng yên.

Trong sweep này, ta giữ các tham số chính cố định: `b = 0.56 s`, `tau = 0.61 s`, và `L = 17.3 m`. Sau đó ta thử ba giá trị `a = 0.30 m`, `0.36 m`, và `0.42 m`.

Câu hỏi của slide này là: nếu chỉ thay đổi kích thước baseline của pedestrian, thì congestion onset sẽ dịch chuyển như thế nào? Dự đoán vật lý là `a` càng lớn thì pedestrian cần nhiều không gian hơn ở mọi vận tốc, nên khả năng đóng gói giảm và tắc nghẽn sẽ xuất hiện sớm hơn.

### Giải thích nội dung và cách dẫn sang biểu đồ

- Slide này chưa phải biểu đồ, mà là setup cho biểu đồ parameter sensitivity ở slide tiếp theo.
- `a` tác động đến mỗi pedestrian ở mọi thời điểm, vì nó không phụ thuộc vào vận tốc.
- Khi density thấp, pedestrian ít khi chạm ràng buộc hard-body, nên thay đổi `a` dự kiến không làm curve khác nhau nhiều.
- Khi density trung bình và cao, hard-body constraint xuất hiện thường xuyên hơn. Lúc này `a` lớn hơn sẽ làm velocity giảm sớm hơn.
- Câu nói để chuyển slide: "Ở slide tiếp theo, ta sẽ thấy đúng xu hướng này trên fundamental diagram: các curve gần nhau ở mật độ thấp, nhưng tách rõ khi mật độ tăng."

### Nếu cần giải thích biểu đồ sweep `a` ở slide tiếp theo

- **Trục x**: density `rho`.
- **Trục y**: mean velocity.
- **Ba đường**: `a = 0.30`, `a = 0.36`, `a = 0.42`.
- **Vùng mật độ thấp**: các đường gần nhau vì pedestrian còn nhiều khoảng trống.
- **Vùng mật độ cao**: `a = 0.42` giảm nhanh nhất, `a = 0.30` giữ velocity cao hơn.
- **Kết luận**: calibrating `a` thay đổi ngưỡng bắt đầu tắc nghẽn ngay cả khi `b` đã giữ ở giá trị best-fit.

### Câu chốt

`b` điều khiển khoảng cách động theo vận tốc, còn `a` điều khiển footprint cơ bản. Muốn fundamental diagram đúng, mô hình cần calibration cả hai thành phần này.
