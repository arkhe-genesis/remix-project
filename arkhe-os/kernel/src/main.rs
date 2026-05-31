#![cfg_attr(not(test), no_std)]
#![cfg_attr(not(test), no_main)]

mod ipc;
mod isolation;
mod memory;
mod scheduler;
mod syscalls;
mod temporal;

#[cfg(not(test))]
use core::panic::PanicInfo;

#[cfg(not(test))]
#[no_mangle]
pub extern "C" fn _start() -> ! {
    // Initialization of kernel systems
    memory::init();
    scheduler::init();
    ipc::init();
    isolation::init();
    temporal::init();

    loop {
        // Idle loop
        scheduler::yield_execution();
    }
}

#[cfg(not(test))]
#[panic_handler]
fn panic(_info: &PanicInfo) -> ! {
    loop {}
}
