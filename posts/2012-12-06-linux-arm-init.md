date: 2012-12-06
layout: post
title: "Linux Arm 初始化分析"
description: ""
category: "学习"
tags: [Linux, Arm, 初始化, kernel]

[原文在此](http://www.linux-arm.org/LinuxBootLoader/SMPBoot)

##Booting ARM Linux SMP on MPCore
对从上电起到一个4核系统的shell命令行界面出现这一过程的理解是很重要的。由于环境配置和可用硬件因平台而异，嵌入式Linux内核启动过程不同于PC环境。例如嵌入式系统中没有PC上面的硬盘和BIOS，而相应的有一个boot minitor和flash存储器。因此，不同硬件架构中启动流程的区别主要存在于程序中发现和载入内核的部分。一旦内核加载到内存中，之后的启动大体流程在所有的CPU架构上都是一样的，区别在于特定的硬件架构上的重载函数。

Linux启动流程可以分为3个阶段。

当我们按下电源开关后，Boot Monitor代码从一个预定义的地址开始执行，地址是NOR flash存储器（0x00000000）。Boot Monitor首先初始化硬件外围设备，如果提供了一个自动的脚本，会自动启动真正的bootloader U-Boot；否则可以在Boot Monitor手动输入合适的命令行参数来启动U-Boot。U-Boot初始化主要的存储器，拷贝压缩后的存放在板子上的NOR flash 存储器，MMC，CompactFlash，或者主机PC中的Linux内核映像（uImage）到主存中，传递给内核初始化的参数后，内核开始执行。首先Linux内核先解压自己，开始初始化自己的数据结构，创建一些用户进程，启动所有的核，最终在用户空间中进入命令行环境。

这是一个简略的内核整个启动流程的介绍。下面，我们详细的介绍每一个阶段的情况并给出相关的内核源码分析。

### System startup (Boot Monitor)

当系统上电或复位时，ARM11 MPCore中的所有CPU从复位向量地址中取得下一条指令到他们的PC寄存器中。在这里，Boot Monitor程序存在的地址就是NOR flash存储器的（0x00000000）。只有CPU0继续执行Boot Monitor代码，第二组CPU（CPU1，CPU2和CPU3）执行一个WFI指令,这个指令主要是循环检测`SYS_FLAGS`寄存器。第二组CPU在Linux内核启动里开始执行有意义的代码，这将在下面的段落中详细介绍。

这个Boot Monitor是标准的ARM程序，根据ARM平台的库编译，在系统启动时运行。

一旦复位，Boot Monitor执行一下动作:

- 执行代码。CPU0执行主要的代码，第二组的CPU执行WFI指令。
- 初始化内存控制器，配置板子的主要外围设备。
- 在内存中设置一个栈。
- 复制自己到主要的存储器--DRAM。
- 内存重映射。
- 根据板子的设置重映射、定向C函数库的I/O路线（输出：UART0或LCD 输入：UART0或键盘）
- 如果自启动脚本存在于NOR flash存储器中并且板子的相关开关已经打开，运行自启动脚本;否则，进入一个Boot Monitor命令行界面。

基本上，板子带的Boot Monitor应用程序类似于PC中的BIOS。它只有有限的功能不能启动一个Linux内核映像。因此，需要额外的bootloader来完成启动进程，也就是U-Boot。U-Boot代码是交叉编译到ARM平台上的烧录到NOR flash存储器中的。最后一步是从BootMonitor命令行启动U-Boot映像。这一步可以使用一个脚本实现，或者手动输入合适的命令。

### Bootloder （U-Boot）

当bootloader被Boot Monitor调用时，它存放在NOR flash存储器。因为内存控制器没有按照U-Boot希望的那样初始化，所以此时它没有访问系统RAM的权限。那么，U-Boot是怎样把自己从flash存储器移动到主存中的呢？

为了获得正常的C环境和运行初始化代码，U-Boot需要分配一个最小化的栈。在ARM11 MPCore中，这是在L1数据缓存中的一个部分中完成的。在这种方式中，缓存被用作在SDRAM控制器设置好前初始化U-Boot的临时数据存储器。接着，U-Boot初始化ARM11 MPCore及其缓存和SCU。下一步，所有的存储器被初步映射了，运行一个简单的内存测试决定SDRAM的大小。最终，bootloader把自己安装在SDRAM的末端，并且通过malloc()函数分配内存供自己和存放板子的全局数据使用。在低地址中，复制了异常向量表。现在，最终的栈被设置起来了。

在这个阶段，U-Boot的第二个部分在主存中并且C环境设置好了。bootloader已经准备好从预先传递的启动参数中指定的地址中启动Linux内核映像。而且，它给内核初始化一个串口或者视频串口。最终，它直接跳转到arch/arm/boot/compressed/head.S文件中的start 标签处，调用内核映像。这个start是Linux内核解压的头部。

bootloader（或者boot monitor/loader的混合体）可以实现很多功能。可是，一个最小的需求集必须实现：

- 配置系统的主存：  
在系统中，Linux内核并不知道RAM的配置。bootloader发现并以机器独立的方式初始化整个内核使用做可变数据存储区的RAM，然后通过使用`ATAG_MEM`参数传递物理内存布局到内核。
- 在正确的内存地址装入内核：  
uImage封装了包含头信息的压缩的Linux内核。头信息包括一个特定的magic数和一个数据区。头和数据通过CRC32校验保证安全。在数据区，存储了映像开始和结束的偏移量。根据它们判断映像的大小，进而决定分配存储区的大小。ARM Linux内核希望被装载在主存的0x7fc0处。
- 初始化一个终端：  
由于在所有平台上为了与目标板进行通讯和内核早期的调试，串口都是必要的，bootloader应该在目标板上初始化并使能一个串口。然后传递相关的终端参数给内核，让内核
识别为已经使能的端口。
- 初始化传递给内核的启动参数：  
bootloader必须以标签的形式描述已经执行的设置，系统内存的大小和布局，和一些其他信息（如下表）并传递给内核。
- 获得ARM Linux机器类型：  
bootloader提供一个简单的独一无二的数字作为ARM系统的机器类型，这个数字用来识别平台。它可以是在源码中定义，也可以板子中读取。机器类型可以从[ARM-Linux project website](http://www.arm.linux.org.uk/developer/machines/)获取。
- 设置合适的寄存器值进入内核：  
最终，在开始Linux内核映像的执行之前，ARM11 MPCore寄存器必须被合适的方式设置：
	- 超级模式（SVC）
	- IRQ 和 FIQ 中断禁止
	- MMU关闭(不需要地址翻译)
	- 数据缓存关闭
	- 指令缓存或者打开或关闭
	- CPU寄存器0=0
	- CPU寄存器1=ARM Linux机器类型
	- CPU寄存器2=参数列表的物理地址

### ARM Linux

如上所述，bootloader跳转到压缩的内核映像代码并通过ATAG传递一些初始化的参数。压缩的内核映像的开始来自于arch/arm/boot/compressed/head.S汇编文件中的start标签。从这一步开始，启动进程包括3个主要的阶段。首先，内核解压自己。然后，处理器依赖的代码执行，初始化CPU和内存。最后，处理器独立的代码执行，通过启动其他所有的ARM11核来启动ARM Linux SMP内核并初始化所有内核组件和数据结构。

这个流程图总结了ARM Linux内核的启动流程：

在Linux SMP环境中，CPU0就像在单处理器环境中一样，为初始化所有资源负责。一旦设置好，访问资源严格按照同步规则来进行，如spinlock。CPU0会配置好启动的页表，因此第二组核从一个Linux的专用段启动，而不是默认的复位向量。当第二组核启动相同的Linux映像时，它们在特定的地方进入Linux中，因此，它们简单的初始化跟自己相关的资源（caches,MMU），不再重复初始化已经配置好的部分，然后执行PID为0的idle进程。

下面是Linux内核进程每一步的介绍：

1.  映像解压
	- U-Boot跳转到arch/arm/boot/compressed/head.S中的start标签
	- 保存U-Boot传递的在r1（CPU的架构ID）和r2（ATAG参数列表的指针）的参数。
	- 关闭中断。执行结构相关代码，如果内核重定位调整地址。
	- 现在C环境设置成功。
	- 调用`cache_on`，找到`proc_types`列表，找出相关的ARM架构，再次打开缓存。对ARM11 MPCore（ARM v6），相应的打开、关闭和刷新缓存操作分别是`__armv4_mmu_cache_on`,`__armv4_mmu_cache_off`,`__armv6_mmu_cache_flush`。
	- 给寄存器和栈指针分配合适的值。例如，r4=内核的起始物理地址 sp=解压代码
	- 检测解压的内核映像是否会覆盖压缩的映像，跳转到合适的路径。
	- 调用arch/arm/boot/compressed/misc.c中的`decompress_kernel()`,进入解压流程。这个函数会在输出终端上打印“Uncompressing Linux...”信息。接着调用gunzip()函数，然后打印“done,booting the kernel”信息。
	- 用`__armv6_mmu_cache_flush`刷新缓存。
	- 用`__armv4_mmu_cache_off`关闭缓存，因为内核初始化的路线希望缓存在开始说是关闭的。
	- 跳转到内核在RAM的开始地方，这个地址存放在r4寄存器里。内核起始地址因平台而异。对ARM11 MPCore，存放在arch/arm/mach-realview/Makefile.boot中的 zreladdr-y变量中。
2.  处理器依赖的特定内核代码：  
	这阶段启动开始点是stext，在arch/arm/kernel/head.S中。当解压器关闭MMU、设置好相关寄存器后，就跳转到这里。在这阶段，下面的事件序列在stext中完成（arch/arm/kernel/head.S）。
	- 切换到Supervisor保护模式并禁止中断。
	- 通过（arch/arm/kernel/head-common.S中）`__lookup_processor_type`查找处理器类型。这将返回一个指向`proc_info_list`列表（定义在arch/arm/include/asm/procinfo.h）的指针。
	- （arch/arm/kernel/head-common.S）`__lookup_machine_type`查找机器类型。这返回一个指向`machine_desc`的结构体。
	- 通过`__create_page_tables`创建页表，设置满足内核运行的页表。也就是说，映射内核的代码部分。
	- 跳转到`__v6_setup`(arch/arm/mm/proc-v6.S),初始化CPU0的TLB，cache和 MMU的状态。
	- 调用`__enable_mmu`,使能MMU，设置一些配置位。然后调用`__turn_mmu_on`（arch/arm/kernel/head.S）
	- 在`__turn_mmu_on`中，设置合适的控制寄存器然后跳转到`__switch_data`,后者执行`__mmap_switched`（arch/arm/kernel/head-common.S）。
	- 在`__mmap_switched`中，数据段复制到RAM，BSS段清空。最终，跳转到`start_kernel()`（init/main.c）。

3.  处理器无关内核代码  
	从这阶段开始，是一组通用的Linux内核硬件架构无关的启动程序。当然也有一些函数是硬件依赖，实际上是重载这些无关的函数。我们主要集中在Linux启动中的SMP部分和ARM11 MPCore怎样初始化CPUs。  
	在`start_kernel()`:(init/main.c)
	- 使用` local_irq_disable() `禁止CPU0上的中断(include/linux/irqflags.h)
	- 使用`lock_kernel()`锁定内核，防止被中断或者高优先级的中断抢占。(include/linux/smp-lock.h)
	- `tick_init()` (kernel/time/tick-common.c)初始化内核tick控制。
	- 激活CPU0。`boot_cpu_init()` (init/main.c)
	- 初始化内存子系统`page_address_init()` (mm/highmem.c)
	- 在终端上使用printk显示内核版本。printk(`linux_banner`) (init/version.c)
	- 使用`setup_arch(&command_line)`设置架构的特定子系统,如内存，I/O，处理器等。这个`command_line`是U-Boot传递给内核的参数列表。 (arch/arm/kernel/setup.c)
		- 在`setup_arch(&command_line) `中，我们执行结构相关代码。对ARM11 MPCore来说，调用`smp_init_cpus() `初始化CPU映射。在这里内核知道系统中有4个核。 (arch/arm/mach-realview/platsmp.c)
		- 使用` cpu_init()`初始化一个CPU（这里是CPU0）,丢掉缓存信息，初始化SMP的特定信息，设置per-cpu栈。(arch/arm/kernel/setup.c)
	- 使用`setup_per_cpu_areas()`设置一个多处理器运行环境。这个函数判断每个CPU要求的内存大小，为每个CPU分配并初始化内存。这样，每一个CPU都有一个区存放自己的数据。 (init/main.c)
	- 使用`smp_prepare_boot_cpu()`允许正在启动的CPU（CPU0）去访问自己存储的初始化后的数据。(arch/arm/kernel/smp.c)
	- `sched_init() `设置Linux调度器 (kernel/sched.c)。
		- 用每个CPU的自己的相关数据初始化一个运行队列。 (kernel/sched.c)
		- 用`init_idle`派生出一个idle 线程供CPU0用。(current, `smp_processor_id()`) (kernel/sched.c)
	- 初始化内存区，如DMA，normal，high memory。` build_all_zonelists()`(mm/page_alloc.c)
	- 使用` parse_early_param()` (init/main.c) and `parse_args()` (kernel/params.c)解析传递给Linux内核的参数。
	- 使用` using init_IRQ()` (arch/arm/kernel/irq.c) and `trap_init()` (arch/arm/kernel/traps.c)初始化中断表、GIC和异常向量跳转表。同时指定处理器与每个中断的关系。
	- 使用`softirq_init()` (kernel/softirq.c)为启动CPU（CPU0）接受来自tasklets的通知做准备。
	- 使用`time_init()`初始化并运行系统定时器。 (arch/arm/kernel/time.c)
	- 使用`local_irq_enable()`使能CPU0上的本地中断。(include/linux/irqflags.h)
	- 使用`console_init()`初始化终端控制台。(drivers/char/tty_io.c)
	- 找出所有内存区中空闲页的总量。`mem_init()` (arch/arm/mm/init.c)
	- 初始化slab分配器。`kmem_cache_init()` (mm/slab.c)
	- 判断CPU时钟的速度。`calibrate_delay()` (init/calibrate.c)
	- 初始化内核内部组件，如页表，slab缓存，vfs，缓冲区，信号队列，最大的线程和进程数等。
	- 初始化proc/filesystem文件系统。 `proc_root_init()` (fs/proc/root.c)
	- 调用`rest_init()`创建进程1。在`rest_init()`中，
		- ` kernel_thread(kernel_init, NULL, CLONE_FS | CLONE_SIGHAND)`创建init 进程，也被叫做Process 1。
		- 创建内核守护线程，它是所有内核线程的父亲，PID是2。`pid = kernel_thread(kthreadd, NULL, CLONE_FS | CLONE_FILES) `(kernel/kthread.c)
		- 释放内核锁（在`start_kernel()`开始时锁定的）。`unlock_kernel()`(include/linux/smp-lock.h)
		- 执行`schedule()`调度指令，开始运行调度器。 (kernel/sched.c)
		- `cpu_idle()`在CPU0上执行CPU idle线程。这把CPU0放入调度器的管理中，直到调度器没有其他的挂起进程要在CPU0上运行才返回。CPU idle线程节省电能保持低功耗。 (arch/arm/kernel/process.c)  
		在` kernel_init()`中：(init/main.c)
			- 开始准备SMP环境。`smp_prepare_cpus()` (arch/arm/mach-realview/platsmp.c)
				- 为当前处理器CPU0使能local timer中断。`local_timer_setup(cpu)` (arch/arm/mach-realview/localtimer.c)
				- 移动相关数据到CPU0自己的存储区。`smp_store_cpu_info(cpu)` (arch/arm/kernel/smp.c)
				- 初始化现在的CPU映射，映射描述了CPU的集合，通知了内核有4个核。`cpu_set(i, cpu_present_map)`
				- 初始化Snoop Control Unit。`scu_enable()` (arch/arm/mach-realview/platsmp.c)
				- 调用` poke_milo() `,准备启动第二组核。 (arch/arm/mach-realview/platsmp.c)
					- 在`poke_milo()`中，它触发其他的CPU执行` realview_secondary_startup` (arch/arm/mach-realview/headsmp.S)
					- 在`realview_secondary_startup `中，第二组核等待一个来自内核（CPU0）的同步信号，表示现在可以被初始化了。当所以的处理器准备好了之后，它们执行`secondary_startup procedure` (arch/arm/mach-realview/headsmp.S)
					- `secondary_startup procedure`做一个类似CPU0启动时做的操作。(arch/arm/mach-realview/headsmp.S)
						- 切到Supervisor保护模式并禁止所有中断。
						- 查找处理器类型
						- 使用`__cpu_up`提供的页表给每一个CPU。
						- 初始化核的TLB，cache，MMU状态。
						- 使能MMU
						- 设置适当的寄存器
						- 跳到`secondary_start_kernel `
						- `secondary_start_kernel`是正式的第二组CPU运行内核的开始。它被看作是一个运行在相关CPU上的内核线程。在这个线程中进行进一步的初始化。
							-  `cpu_init()`初始化CPU。丢弃缓存信息，初始化SMP特定信息，设置per-cpu栈。 (arch/arm/kernel/setup.c)
							-  与CPU0的启动线程同步，使能一些中断，如timer irq。`platform_secondary_init(cpu) `(arch/arm/mach-realview/platsmp.c)
							-  使能local中断。` local_irq_enable()  local_fiq_enable() ` (include/linux/irqflags.h)
							-  设置local timer。 `local_timer_setup(cpu)` (arch/arm/mach-realview/localtimer.c)
							-  判断CPU时钟的速度。`calibrate_delay()` (init/calibrate.c)
							-  移动相关数据到CPU自己的存储区。`smp_store_cpu_info(cpu)` (arch/arm/kernel/smp.c)
							-  执行idle线程
			- 调用 `smp_init()` (init/main.c)
				- 调用`cpu_up(cpu)`启动每一个离线的CPU。 (arch/arm/kernel/smp.c)
					- 使用`fork_idle(cpu)`手工创建一个新的idle线程，分配到相应核的数据结构。
					- 分配初始化的页表到允许的CPU，来安全的使能MMU。
					- 通知第二组核发现自己的栈和页表。
					- 启动第二组CPU `boot_secondary(cpu,idle)` (arch/arm/mach-realview/platsmp.c)
				- 打印内核信息“SMP: Total of 4 processors activated (334.02 BogoMIPS?)” `smp_cpus_done(max_cpus)` (arch/arm/kernel/smp.c)
			- 调用`sched_init_smp()` (kernel/sched.c)
				- `arch_init_sched_domains(&cpu_online_map)`构建调度域,设置多核的拓扑结构(kernel/sched.c)
				- 检查有多少个在线的CPU存在，调整合适的调度粒度值。`sched_init_granularity()` (kernel/sched.c)
			- 调用` do_basic_setup()`函数， `driver_init()` (drivers/base/init.c)初始化驱动模型，`init_workqueues()`初始化工作队列。最终调用` do_initcalls ()`初始化设备内建驱动。
			- 调用`init_post()` (init/main.c),切换到用户模式调用下面的程序。
				- `run_init_process("/sbin/init");`
				- `run_init_process("/etc/init");`
				- `run_init_process("/bin/init");`
				- `run_init_process("/bin/sh");`
			`/sbin/init`执行并在终端打印一些信息，把 控制权交给控制台并保证激活状态。



## 初始化流程

分析ARM下的Linux内核初始化  
从`start_kernel()`开始分析，前面的暂时没有看。

	{% highlight c %}
	asmlinkage void __init start_kernel(void)
	{
		char * command_line;
		extern const struct kernel_param __start___param[], __stop___param[];

		smp_setup_processor_id();

		/*
		 * Need to run as early as possible, to initialize the
		 * lockdep hash:
		 */
		lockdep_init();
		debug_objects_early_init();

		/*
		 * Set up the the initial canary ASAP:
		 */
		boot_init_stack_canary();

		cgroup_init_early();

		local_irq_disable();
		early_boot_irqs_disabled = true;

	/*
	 * Interrupts are still disabled. Do necessary setups, then
	 * enable them
	 */
		tick_init();
		boot_cpu_init();
		page_address_init();
		printk(KERN_NOTICE "%s", linux_banner);
		setup_arch(&command_line);
		mm_init_owner(&init_mm, &init_task);
		mm_init_cpumask(&init_mm);
		setup_command_line(command_line);
		setup_nr_cpu_ids();
		setup_per_cpu_areas();
		smp_prepare_boot_cpu();	/* arch-specific boot-cpu hooks */

		build_all_zonelists(NULL);
		page_alloc_init();

		printk(KERN_NOTICE "Kernel command line: %s\n", boot_command_line);
		parse_early_param();
		parse_args("Booting kernel", static_command_line, __start___param,
			   __stop___param - __start___param,
			   &unknown_bootoption);

		jump_label_init();

		/*
		 * These use large bootmem allocations and must precede
		 * kmem_cache_init()
		 */
		setup_log_buf(0);
		pidhash_init();
		vfs_caches_init_early();
		sort_main_extable();
		trap_init();
		mm_init();

		/*
		 * Set up the scheduler prior starting any interrupts (such as the
		 * timer interrupt). Full topology setup happens at smp_init()
		 * time - but meanwhile we still have a functioning scheduler.
		 */
		sched_init();
		/*
		 * Disable preemption - early bootup scheduling is extremely
		 * fragile until we cpu_idle() for the first time.
		 */
		preempt_disable();
		if (!irqs_disabled()) {
			printk(KERN_WARNING "start_kernel(): bug: interrupts were "
					"enabled *very* early, fixing it\n");
			local_irq_disable();
		}
		idr_init_cache();
		perf_event_init();
		rcu_init();
		radix_tree_init();
		/* init some links before init_ISA_irqs() */
		early_irq_init();
		/*IRQ的初始化，该函数调用machine_desc->init_irq();machine_desc是配置内核选项时指定的。比如配置时选择system type为TI OMAP4 ，则根据在Arch/Arm/Mach-omap2下的定义。调用gic_init_irq()函数完成相应的初始化。*/
		init_IRQ();
		prio_tree_init();
		/**/
		init_timers();
		hrtimers_init();
		softirq_init();
		timekeeping_init();
		/*调用machine_desc->timer->init(),同上面init_IRQ()一样，调用omap4_timer_init()函数完成初始化。这个初始化只是初始化GPTimer，之后会进行localtimer的初始化，当第二个核启动后，会进行localtimer的初始化*/
		time_init();
		profile_init();
		call_function_init();
		if (!irqs_disabled())
			printk(KERN_CRIT "start_kernel(): bug: interrupts were "
					 "enabled early\n");
		early_boot_irqs_disabled = false;
		local_irq_enable();

		/* Interrupts are enabled now so all GFP allocations are safe. */
		gfp_allowed_mask = __GFP_BITS_MASK;

		kmem_cache_init_late();

		/*
		 * HACK ALERT! This is early. We're enabling the console before
		 * we've done PCI setups etc, and console_init() must be aware of
		 * this. But we do want output early, in case something goes wrong.
		 */
		console_init();
		if (panic_later)
			panic(panic_later, panic_param);

		lockdep_info();

		/*
		 * Need to run this when irqs are enabled, because it wants
		 * to self-test [hard/soft]-irqs on/off lock inversion bugs
		 * too:
		 */
		locking_selftest();

	#ifdef CONFIG_BLK_DEV_INITRD
		if (initrd_start && !initrd_below_start_ok &&
		    page_to_pfn(virt_to_page((void *)initrd_start)) < min_low_pfn) {
			printk(KERN_CRIT "initrd overwritten (0x%08lx < 0x%08lx) - "
			    "disabling it.\n",
			    page_to_pfn(virt_to_page((void *)initrd_start)),
			    min_low_pfn);
			initrd_start = 0;
		}
	#endif
		page_cgroup_init();
		enable_debug_pagealloc();
		debug_objects_mem_init();
		kmemleak_init();
		setup_per_cpu_pageset();
		numa_policy_init();
		if (late_time_init)
			late_time_init();
		sched_clock_init();
		calibrate_delay();
		pidmap_init();
		anon_vma_init();
	#ifdef CONFIG_X86
		if (efi_enabled)
			efi_enter_virtual_mode();
	#endif
		thread_info_cache_init();
		cred_init();
		fork_init(totalram_pages);
		proc_caches_init();
		buffer_init();
		key_init();
		security_init();
		dbg_late_init();
		vfs_caches_init(totalram_pages);
		signals_init();
		/* rootfs populating might need page-writeback */
		page_writeback_init();
	#ifdef CONFIG_PROC_FS
		proc_root_init();
	#endif
		cgroup_init();
		cpuset_init();
		taskstats_init_early();
		delayacct_init();

		check_bugs();

		acpi_early_init(); /* before LAPIC and SMP init */
		sfi_init_late();

		ftrace_init();

		/* Do the rest non-__init'ed, we're now alive */
		/*对于双核系统而言，第二个核的初始化来自这个函数。该函数调用kernel_init，进而执行其中的smp_init(如果配置了SMP选项的话)。这里通过几个cpu_up函数，最终调用体系结构相关函数__cpu_up(),这个函数完成为新核初始化页表、设置task struct
		指针，开启MMU等。然后这个函数调用boot_secondary函数，完成第二个核的启动。在函数boot_secondary中，调用gic_raise_softirq，使用软中断的方式，启动第二个核，调用secondary_start_kernel（这部分大致如此）*/
		rest_init();
	}
	{% endhighlight %}

 
